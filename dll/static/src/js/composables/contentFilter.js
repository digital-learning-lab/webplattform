import { debounce } from 'lodash';
import { computed, ref, watch } from 'vue';

import { useAxios } from './axios';
import { useQuery } from './query';

const { updateQueryString, query } = useQuery();

export function useContentFilter() {
  const initArray = (val) => {
    return Array.isArray(val) ? val : val ? [val] : [];
  }
 
  const { axios } = useAxios();

  const currentPage = ref(query.page || 1);
  const dataUrl = ref(null);
  const queryParams = ref(query || {});
  const contents = ref([]);
  const loading = ref(true);
  const sorting = ref(query.sorting || '-latest');
  const q = ref(query.q || '');
  const competences = ref(initArray(query.competences));
  const currentResponse = ref(null);
  const mobileFilterExpanded = ref(false);

  const windowDom = computed(() => {
    return window;
  });

  const loggedIn = computed(() => {
    return windowDom.value.loggedIn;
  });

  const getSubjects = () => window.subjectFilter;
  const mobileFilterToggle = computed(() => {
    return mobileFilterExpanded.value ? 'Filter einklappen' : 'Filter ausklappen';
  })


  const getParams = (page) => {
    return {
      competence: window.competenceSlug,
      competences: competences.value,
      page: Number.isInteger(page) ? page : 1,
      q: q.value,
      sorting: sorting.value,
      ...queryParams.value
    };
  };

  const updateContents = async (page) => {
    currentResponse.value = null;
    const params = getParams(page);
    loading.value = true;

    if (!page || typeof page === 'object') {
      // Reset page to 1 if there is no page given or page object is an event (object)
      currentPage.value = 1;
    } else {
      currentPage.value = page;
    }

    await axios
      .get(dataUrl.value, {
        params
      })
      .then((response) => {
        window.scroll(0, 0);
        updateQueryString(params);
        contents.value = response.data.results;
        currentResponse.value = response;
      })
      .catch((error) => {
        console.log(error);
      })
      .finally(() => {
        loading.value = false;
      });

    return currentResponse.value;
  };

  //  --------------------------------------------------------------------------
  //  watchers
  //  --------------------------------------------------------------------------
  watch(q, () => {
    debouncedUpdate();
  });

  watch(competences, () => {
    updateContents();
  });

  const debouncedUpdate = debounce(updateContents, 500);

  return {
    axios,
    competences,
    contents,
    currentPage,
    currentResponse,
    dataUrl,
    debouncedUpdate,
    getSubjects,
    loading,
    loggedIn,
    q,
    queryParams,
    sorting,
    updateContents,
    initArray,
    mobileFilterExpanded,
    mobileFilterToggle
  };
}
