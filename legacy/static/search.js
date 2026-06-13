// Search page JavaScript
const API_BASE = '';

async function performSearch() {
    const query = document.getElementById('searchInput').value.trim();
    if (!query) return;

    const resultsDiv = document.getElementById('searchResults');
    resultsDiv.textContent = '검색 중...';

    try {
        const res = await fetch(`${API_BASE}/api/search?q=${encodeURIComponent(query)}&limit=100`);
        const data = await res.json();

        resultsDiv.textContent = '';

        if (data.total === 0) {
            const noResults = document.createElement('p');
            noResults.className = 'no-results';
            noResults.textContent = '검색 결과가 없습니다';
            resultsDiv.appendChild(noResults);
            return;
        }

        const summary = document.createElement('p');
        summary.className = 'search-summary';
        summary.textContent = `${data.total}개의 결과를 찾았습니다`;
        resultsDiv.appendChild(summary);

        data.results.forEach(commit => {
            const item = document.createElement('div');
            item.className = 'search-result-item';

            const header = document.createElement('div');
            header.className = 'result-header';

            const project = document.createElement('span');
            project.className = 'result-project';
            project.textContent = commit.project_name;

            const type = document.createElement('span');
            type.className = `result-type type-${commit.type}`;
            type.textContent = commit.type;

            const date = document.createElement('span');
            date.className = 'result-date';
            date.textContent = commit.date;

            header.appendChild(project);
            header.appendChild(type);
            header.appendChild(date);

            const title = document.createElement('h4');
            title.className = 'result-title';
            title.textContent = commit.title;

            const meta = document.createElement('div');
            meta.className = 'result-meta';
            meta.textContent = `${commit.files_changed || 0} files, +${commit.lines_added || 0} -${commit.lines_deleted || 0}`;

            item.appendChild(header);
            item.appendChild(title);
            item.appendChild(meta);
            resultsDiv.appendChild(item);
        });

    } catch (error) {
        console.error('Search failed:', error);
        resultsDiv.textContent = '검색 실패: ' + error.message;
    }
}

// Enter key search
document.getElementById('searchInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') performSearch();
});
