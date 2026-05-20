export interface WatchlistMovie {
  id: number;
  poster: string | null;
  movieId: number;
  title: string | null;
  providers: WatchProvider[];
  voteAverage: number;
}

export interface WatchedMovie {
  id: number;
  poster: string | null;
  movieId: number;
  title: string | null;
  rating: number | null;
}

export type WatchProvider = {
  providerName: string | null;
  logoPath: string | null;
};

export interface MovieCreate {
  title: string;
  genre: string;
  rating: number;
  description?: string;
}
