// Dev Log Admin - Main JavaScript
const API_BASE = '';

// Dashboard page
async function loadDashboard() {
    try {
        const [projectsRes, statsRes] = await Promise.all([
            fetch(`${API_BASE}/api/projects`),
            fetch(`${API_BASE}/api/stats/overview`)
        ]);

        const projects = await projectsRes.json();
        const stats = await statsRes.json();

        // Update stats
        document.getElementById('totalProjects').textContent = stats.total_projects;
        document.getElementById('totalCommits').textContent = stats.total_commits.toLocaleString();
        document.getElementById('recentActivity').textContent =
            stats.recent_activity[0]?.date.substring(0, 10) || 'N/A';

        // Render charts and lists
        renderTypeChart(stats.commits_by_type);
        renderProjects(projects);
        renderRecentActivity(stats.recent_activity);

    } catch (error) {
        console.error('Failed to load dashboard:', error);
        alert('데이터 로딩 실패: ' + error.message);
    }
}

function renderTypeChart(typeStats) {
    const typeColors = {
        'feat': '#10b981', 'fix': '#ef4444', 'refactor': '#8b5cf6',
        'docs': '#3b82f6', 'test': '#f59e0b', 'chore': '#6b7280',
        'ci': '#06b6d4', 'perf': '#ec4899'
    };

    const chart = document.getElementById('typeChart');
    const total = Object.values(typeStats).reduce((a, b) => a + b, 0);

    chart.textContent = '';
    Object.entries(typeStats)
        .sort((a, b) => b[1] - a[1])
        .forEach(([type, count]) => {
            const percentage = (count / total * 100).toFixed(1);

            const barDiv = document.createElement('div');
            barDiv.className = 'type-bar';

            const labelDiv = document.createElement('div');
            labelDiv.className = 'type-label';

            const nameSpan = document.createElement('span');
            nameSpan.className = 'type-name';
            nameSpan.textContent = type;

            const countSpan = document.createElement('span');
            countSpan.className = 'type-count';
            countSpan.textContent = `${count} (${percentage}%)`;

            labelDiv.appendChild(nameSpan);
            labelDiv.appendChild(countSpan);

            const progressDiv = document.createElement('div');
            progressDiv.className = 'type-progress';

            const fillDiv = document.createElement('div');
            fillDiv.className = 'type-fill';
            fillDiv.style.width = `${percentage}%`;
            fillDiv.style.backgroundColor = typeColors[type] || '#6b7280';

            progressDiv.appendChild(fillDiv);
            barDiv.appendChild(labelDiv);
            barDiv.appendChild(progressDiv);
            chart.appendChild(barDiv);
        });
}

function renderProjects(projects) {
    const grid = document.getElementById('projectsGrid');
    grid.textContent = '';

    projects.forEach(proj => {
        const card = document.createElement('div');
        card.className = 'project-card';

        const header = document.createElement('div');
        header.className = 'project-header';
        const h3 = document.createElement('h3');
        h3.textContent = proj.name;
        const commits = document.createElement('span');
        commits.className = 'project-commits';
        commits.textContent = `${proj.total_commits} commits`;
        header.appendChild(h3);
        header.appendChild(commits);

        const desc = document.createElement('p');
        desc.className = 'project-desc';
        desc.textContent = proj.description || '';

        const techDiv = document.createElement('div');
        techDiv.className = 'project-tech';
        proj.tech_stack.forEach(tech => {
            const tag = document.createElement('span');
            tag.className = 'tech-tag';
            tag.textContent = tech;
            techDiv.appendChild(tag);
        });

        const actions = document.createElement('div');
        actions.className = 'project-actions';
        const viewLink = document.createElement('a');
        viewLink.href = `/project.html?slug=${proj.slug}`;
        viewLink.className = 'btn-primary';
        viewLink.textContent = 'View Details →';
        actions.appendChild(viewLink);

        if (proj.html_url) {
            const htmlBtn = document.createElement('button');
            htmlBtn.className = 'btn-secondary';
            htmlBtn.textContent = 'Open HTML ↗';
            htmlBtn.onclick = async () => {
                try {
                    const response = await fetch(`${API_BASE}/api/projects/${proj.slug}/open`);
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
            };
            actions.appendChild(htmlBtn);
        }

        // Terminal button
        const terminalBtn = document.createElement('button');
        terminalBtn.className = 'btn-secondary';
        terminalBtn.textContent = '🖥️ Terminal';
        terminalBtn.onclick = async () => {
            try {
                const response = await fetch(`${API_BASE}/api/projects/${proj.slug}/terminal`);
                if (response.ok) {
                    const data = await response.json();
                    console.log(data.message);
                } else {
                    const error = await response.json();
                    alert('Failed to open terminal: ' + error.detail);
                }
            } catch (error) {
                console.error('Error opening terminal:', error);
                alert('Error opening terminal: ' + error.message);
            }
        };
        actions.appendChild(terminalBtn);

        const footer = document.createElement('div');
        footer.className = 'project-footer';
        footer.textContent = `Last synced: ${proj.last_synced_at ? new Date(proj.last_synced_at).toLocaleString('ko-KR') : 'Never'}`;

        card.appendChild(header);
        card.appendChild(desc);
        card.appendChild(techDiv);
        card.appendChild(actions);
        card.appendChild(footer);
        grid.appendChild(card);
    });
}

function renderRecentActivity(activity) {
    const list = document.getElementById('recentList');
    list.textContent = '';

    activity.forEach(commit => {
        const item = document.createElement('div');
        item.className = 'recent-item';

        const date = document.createElement('div');
        date.className = 'recent-date';
        date.textContent = commit.date;

        const project = document.createElement('div');
        project.className = 'recent-project';
        project.textContent = commit.project_name;

        const type = document.createElement('div');
        type.className = `recent-type type-${commit.type}`;
        type.textContent = commit.type;

        const title = document.createElement('div');
        title.className = 'recent-title';
        title.textContent = commit.title;

        item.appendChild(date);
        item.appendChild(project);
        item.appendChild(type);
        item.appendChild(title);
        list.appendChild(item);
    });
}

function reloadData() {
    if (confirm('데이터를 다시 로드하시겠습니까?')) {
        location.reload();
    }
}

// Load on page load
if (document.getElementById('projectsGrid')) {
    loadDashboard();
}
