// Project Details Page JavaScript
const API_BASE = '';
const urlParams = new URLSearchParams(window.location.search);
const projectSlug = urlParams.get('slug');
let currentPage = 0;
const pageSize = 20;

async function loadProjectDetails() {
    try {
        const response = await fetch(`${API_BASE}/api/projects/${projectSlug}`);
        const project = await response.json();

        document.getElementById('projectName').textContent = project.name;
        document.getElementById('projectDesc').textContent = project.description || 'No description';

        const meta = document.getElementById('projectMeta');
        meta.textContent = '';

        // Tech stack
        const techDiv = document.createElement('div');
        techDiv.className = 'project-tech';
        project.tech_stack.forEach(tech => {
            const tag = document.createElement('span');
            tag.className = 'tech-tag';
            tag.textContent = tech;
            techDiv.appendChild(tag);
        });
        meta.appendChild(techDiv);

        // Stats
        const statsDiv = document.createElement('div');
        statsDiv.style.marginTop = '1rem';
        statsDiv.style.color = '#666';

        const statsStrong1 = document.createElement('strong');
        statsStrong1.textContent = 'Total Commits:';
        statsDiv.appendChild(statsStrong1);
        statsDiv.appendChild(document.createTextNode(` ${project.total_commits} | `));

        const statsStrong2 = document.createElement('strong');
        statsStrong2.textContent = 'Last Synced:';
        statsDiv.appendChild(statsStrong2);
        statsDiv.appendChild(document.createTextNode(` ${new Date(project.last_synced_at).toLocaleString('ko-KR')}`));

        meta.appendChild(statsDiv);

        // Action buttons
        const actionsDiv = document.createElement('div');
        actionsDiv.style.marginTop = '0.5rem';

        const openBtn = document.createElement('button');
        openBtn.className = 'btn-primary';
        openBtn.textContent = 'Open HTML Dashboard ↗';
        openBtn.onclick = openProjectHTML;
        actionsDiv.appendChild(openBtn);

        if (project.repository_url) {
            const repoLink = document.createElement('a');
            repoLink.href = project.repository_url;
            repoLink.target = '_blank';
            repoLink.className = 'btn-secondary';
            repoLink.textContent = 'View Repository →';
            actionsDiv.appendChild(repoLink);
        }

        meta.appendChild(actionsDiv);

        loadCommits();
    } catch (error) {
        console.error('Failed to load project:', error);
        alert('프로젝트 로딩 실패: ' + error.message);
    }
}

async function loadCommits() {
    const type = document.getElementById('typeFilter').value;
    const search = document.getElementById('searchInput').value;

    try {
        let url = `${API_BASE}/api/projects/${projectSlug}/commits?limit=${pageSize}&offset=${currentPage * pageSize}`;
        if (type) url += `&type=${type}`;
        if (search) url += `&search=${encodeURIComponent(search)}`;

        const response = await fetch(url);
        const data = await response.json();

        renderCommits(data.commits);
        renderPagination(data.total);
    } catch (error) {
        console.error('Failed to load commits:', error);
        alert('커밋 로딩 실패: ' + error.message);
    }
}

function renderCommits(commits) {
    const list = document.getElementById('commitsList');
    list.textContent = '';

    if (commits.length === 0) {
        const emptyMsg = document.createElement('p');
        emptyMsg.style.textAlign = 'center';
        emptyMsg.style.color = '#666';
        emptyMsg.textContent = 'No commits found';
        list.appendChild(emptyMsg);
        return;
    }

    commits.forEach(commit => {
        const item = document.createElement('div');
        item.className = 'commit-item';
        item.style.border = '1px solid #e5e7eb';
        item.style.borderRadius = '8px';
        item.style.padding = '1rem';
        item.style.marginBottom = '1rem';

        // Header with type and metadata
        const header = document.createElement('div');
        header.style.display = 'flex';
        header.style.alignItems = 'center';
        header.style.gap = '0.5rem';
        header.style.marginBottom = '0.5rem';

        const typeSpan = document.createElement('span');
        typeSpan.className = `recent-type type-${commit.type}`;
        typeSpan.textContent = commit.type;
        header.appendChild(typeSpan);

        if (commit.log_number) {
            const logNum = document.createElement('span');
            logNum.style.color = '#666';
            logNum.style.fontSize = '0.875rem';
            logNum.textContent = `#${commit.log_number}`;
            header.appendChild(logNum);
        }

        if (commit.commit_hash) {
            const hash = document.createElement('code');
            hash.style.background = '#f3f4f6';
            hash.style.padding = '0.125rem 0.5rem';
            hash.style.borderRadius = '4px';
            hash.style.fontSize = '0.75rem';
            hash.textContent = commit.commit_hash.substring(0, 7);
            header.appendChild(hash);
        }

        item.appendChild(header);

        // Title
        const title = document.createElement('h4');
        title.style.margin = '0 0 0.5rem 0';
        title.style.fontSize = '1rem';
        title.textContent = commit.title;
        item.appendChild(title);

        // Details
        const details = document.createElement('div');
        details.style.fontSize = '0.875rem';
        details.style.color = '#666';

        if (commit.author_name) {
            details.appendChild(document.createTextNode(`👤 ${commit.author_name} · `));
        }
        details.appendChild(document.createTextNode(`📅 ${commit.date}`));

        if (commit.files_changed > 0) {
            details.appendChild(document.createTextNode(` · 📁 ${commit.files_changed} files`));
        }
        if (commit.lines_added > 0) {
            const added = document.createElement('span');
            added.style.color = '#10b981';
            added.textContent = ` · +${commit.lines_added}`;
            details.appendChild(added);
        }
        if (commit.lines_deleted > 0) {
            const deleted = document.createElement('span');
            deleted.style.color = '#ef4444';
            deleted.textContent = ` · -${commit.lines_deleted}`;
            details.appendChild(deleted);
        }

        item.appendChild(details);
        list.appendChild(item);
    });
}

function renderPagination(total) {
    const totalPages = Math.ceil(total / pageSize);
    const pagination = document.getElementById('pagination');
    pagination.textContent = '';

    if (totalPages <= 1) {
        return;
    }

    const prevBtn = document.createElement('button');
    prevBtn.textContent = '← Previous';
    prevBtn.disabled = currentPage === 0;
    prevBtn.onclick = () => changePage(currentPage - 1);
    pagination.appendChild(prevBtn);

    const pageInfo = document.createElement('span');
    pageInfo.style.margin = '0 1rem';
    pageInfo.textContent = `Page ${currentPage + 1} of ${totalPages}`;
    pagination.appendChild(pageInfo);

    const nextBtn = document.createElement('button');
    nextBtn.textContent = 'Next →';
    nextBtn.disabled = currentPage >= totalPages - 1;
    nextBtn.onclick = () => changePage(currentPage + 1);
    pagination.appendChild(nextBtn);
}

function changePage(page) {
    currentPage = page;
    loadCommits();
}

function handleSearch(event) {
    if (event.key === 'Enter') {
        currentPage = 0;
        loadCommits();
    }
}

async function openProjectHTML() {
    try {
        const response = await fetch(`${API_BASE}/api/projects/${projectSlug}/open`);
        if (response.ok) {
            const data = await response.json();
            console.log(data.message);
        } else {
            const error = await response.json();
            alert('Failed to open HTML: ' + error.detail);
        }
    } catch (error) {
        console.error('Error opening HTML:', error);
        alert('Error opening HTML: ' + error.message);
    }
}

// Load on page load
if (projectSlug) {
    loadProjectDetails();
} else {
    alert('No project specified');
    window.location.href = '/';
}
