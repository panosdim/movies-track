export interface TmdbMovie {
  id: number;
  title: string;
  poster_path: string | null;
  release_date: string;
  vote_average: number;
  popularity: number;
  overview: string;
  genre_ids: number[];
}

export interface TmdbPopularResponse {
  page: number;
  results: TmdbMovie[];
  total_pages: number;
  total_results: number;
}
