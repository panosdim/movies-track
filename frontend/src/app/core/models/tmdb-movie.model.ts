export interface TmdbMovie {
  id: number;
  title: string;
  posterPath: string | null;
  releaseDate: string;
  voteAverage: number;
  popularity: number;
  overview: string;
  genreIds: number[];
}

export interface TmdbPopularResponse {
  page: number;
  results: TmdbMovie[];
  totalPages: number;
  totalResults: number;
}
