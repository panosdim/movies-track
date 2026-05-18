export interface Movie {
  id: number;
  poster: string | null;
  movieId: number;
  title: string | null;
  watched: boolean | null;
  rating: number | null;
  providers: WatchProvider[];
  voteAverage: number;
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
