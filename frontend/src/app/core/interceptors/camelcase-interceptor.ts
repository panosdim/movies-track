import { HttpInterceptorFn, HttpResponse } from '@angular/common/http';
import { map } from 'rxjs';
import camelcaseKeys from 'camelcase-keys';

export const camelcaseInterceptor: HttpInterceptorFn = (req, next) => {
  return next(req).pipe(
    map((event) => {
      if (event instanceof HttpResponse && event.body) {
        const camelCasedBody = camelcaseKeys(event.body, { deep: true });
        return event.clone({ body: camelCasedBody });
      }
      return event;
    }),
  );
};
