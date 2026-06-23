// environment.ts (for development)
import { environmentBase } from './environment.base';

export const environment = {
  ...environmentBase,
  apiUrl: 'https://movies.deltasw.eu/api/v1',
};
