import queryString from 'query-string';

export function useQuery() {
  const updateQueryString = (params) => {
    Object.keys(params).forEach((key) => (params[key] === null || params[key] === '') && delete params[key]);

    if (params) {
      window.history.pushState({}, '', location.pathname + '?' + queryString.stringify(params));
    }
  };
  const query = queryString.parse(location.search, {
    parseBooleans: true
  });

  return { updateQueryString, query };
}
