export interface Movie {
  id: number;
  title: string;
  genre: string;
  rating: number;
  description?: string;
}

export interface MovieCreate {
  title: string;
  genre: string;
  rating: number;
  description?: string;
}
