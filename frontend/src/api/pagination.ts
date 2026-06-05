export type PaginationParams = {
  page?: number;
  page_size?: number;
};

export type PaginatedResponse<T> = {
  items: T[];
  total_items: number;
  start_index: number;
  end_index: number;
  total_pages: number;
  current_page: number;
  current_page_size: number;
};

export type ListResponse<T> = T[] | PaginatedResponse<T>;

export function isPaginatedResponse<T>(
  response: ListResponse<T>,
): response is PaginatedResponse<T> {
  return !Array.isArray(response) && Array.isArray(response.items);
}

export function buildPaginationQuery(params?: PaginationParams) {
  const searchParams = new URLSearchParams();

  if (params?.page !== undefined) {
    searchParams.set("page", String(params.page));
  }

  if (params?.page_size !== undefined) {
    searchParams.set("page_size", String(params.page_size));
  }

  const query = searchParams.toString();

  return query ? `?${query}` : "";
}
