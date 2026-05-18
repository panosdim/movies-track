export interface Movie {
  id: number;
  poster: string | null;
  movieId: number;
  title: string | null;
  watched: boolean | null;
  rating: number;
  userScore: number | null;
  watchInfo: WatchProvider[];
}

export type WatchProvider = {
  providerName: String | null;
  logoPath: String | null;
};

export interface MovieCreate {
  title: string;
  genre: string;
  rating: number;
  description?: string;
}
