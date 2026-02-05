// API Client for Dev Log Admin Backend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8100';

class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new ApiError(response.status, `API Error: ${response.statusText}`);
  }

  return response.json();
}

// Projects API
export const projectsApi = {
  list: () => fetchApi<import('@/types').Project[]>('/api/projects'),

  get: (slug: string) => fetchApi<import('@/types').Project>(`/api/projects/${slug}`),

  getCommits: (
    slug: string,
    params?: { limit?: number; offset?: number; type?: string; search?: string }
  ) => {
    const searchParams = new URLSearchParams();
    if (params?.limit) searchParams.set('limit', params.limit.toString());
    if (params?.offset) searchParams.set('offset', params.offset.toString());
    if (params?.type) searchParams.set('type', params.type);
    if (params?.search) searchParams.set('search', params.search);

    const query = searchParams.toString();
    return fetchApi<import('@/types').CommitsResponse>(
      `/api/projects/${slug}/commits${query ? `?${query}` : ''}`
    );
  },

  openHtml: (slug: string) => fetchApi<{ status: string; message: string }>(`/api/projects/${slug}/open`),

  openTerminal: (slug: string) =>
    fetchApi<{ status: string; message: string }>(`/api/projects/${slug}/terminal`),
};

// Commits API
export const commitsApi = {
  get: (id: number) => fetchApi<import('@/types').Commit>(`/api/commits/${id}`),

  search: (params: {
    q: string;
    project?: string;
    type?: string;
    limit?: number;
    offset?: number;
  }) => {
    const searchParams = new URLSearchParams();
    searchParams.set('q', params.q);
    if (params.project) searchParams.set('project', params.project);
    if (params.type) searchParams.set('type', params.type);
    if (params.limit) searchParams.set('limit', params.limit.toString());
    if (params.offset) searchParams.set('offset', params.offset.toString());

    return fetchApi<import('@/types').SearchResult>(`/api/search?${searchParams.toString()}`);
  },
};

// Stats API
export const statsApi = {
  overview: () => fetchApi<import('@/types').OverviewStats>('/api/stats/overview'),

  timeline: (days?: number) => {
    const query = days ? `?days=${days}` : '';
    return fetchApi<import('@/types').TimelineStats>(`/api/stats/timeline${query}`);
  },
};

// Health API
export const healthApi = {
  check: () => fetchApi<{ status: string; database: string }>('/health'),
};

export { ApiError };
