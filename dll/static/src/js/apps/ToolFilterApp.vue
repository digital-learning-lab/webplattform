<template>
  <div class="row mt-5 mb-5">
    <div class="col col-12 col-lg-5 col-xl-4 mb-4">
      <div class="section-info">
        <form id="filterForm" action="" class="collapse d-lg-block">
          <h2>Filtern nach</h2>
          <h3 class="form-subhead">Schlagwortsuche</h3>
          <input v-model="q" type="text" name="searchTerm" class="form-control" @keydown="preventEnter" />

          <div v-if="!dltFeaturesEnabled">
            <h3 class="form-subhead">Tool-Funktionen</h3>
            <ul class="list-unstyled">
              <li v-for="(toolFunction, index) in functionsFilter" :key="index" class="form-check">
                <input
                  :id="'toolFunction' + toolFunction.id"
                  v-model="toolFunctions"
                  type="checkbox"
                  class="form-check-input"
                  :value="toolFunction.id"
                  name="toolFunction"
                  @change="debouncedUpdate"
                />
                <label class="form-check-label" :for="'toolFunction' + toolFunction.id">{{ toolFunction.title }}</label>
              </li>
            </ul>
          </div>
          <div v-if="dltFeaturesEnabled">
            <h3 class="form-subhead">Potentiale</h3>
            <ul class="list-unstyled">
              <li v-for="(potential, index) in potentialFilter" :key="index" class="form-check">
                <input
                  :id="'potential' + potential.value"
                  v-model="potentials"
                  type="checkbox"
                  class="form-check-input"
                  :value="potential.value"
                  name="potential"
                />
                <label class="form-check-label" :for="'potential' + potential.value">{{ potential.name }}</label>
              </li>
            </ul>
          </div>
          <div v-if="loggedIn && dltFeaturesEnabled">
            <h3 class="form-subhead">Meine favorisierten Tools</h3>
            <ul class="list-unstyled">
              <li class="form-check">
                <input
                  id="favorites-checkbox"
                  v-model="favorites"
                  type="checkbox"
                  class="form-check-input"
                  name="favorites"
                  @change="debouncedUpdate"
                />
                <label class="form-check-label" for="favorites-checkbox">Anzeigen</label>
              </li>
            </ul>
          </div>
          <div>
            <h3 class="form-subhead">Fächerbezug</h3>
            <select id="subject" v-model="subject" name="subject" class="form-control" @change="updateContents">
              <option value="" selected>--------</option>
              <option v-for="(innerSubject, index) in getSubjects()" :key="index" :value="innerSubject.value">
                {{ innerSubject.name }}
              </option>
            </select>
          </div>
          <div>
            <h3 class="form-subhead">Datenschutz</h3>
            <select
              id="dataPrivacy"
              v-model="dataPrivacy"
              name="dataPrivacy"
              class="form-control"
              @change="updateContents"
            >
              <option value="" selected>--------</option>
              <option v-for="(privacy, index) in dataPrivacyOptions" :key="index" :value="privacy.value">
                {{ privacy.name }}
              </option>
            </select>
          </div>
          <div>
            <h3 class="form-subhead">Anwendung:</h3>
            <ul class="list-unstyled">
              <li class="form-check">
                <input
                  id="application-1"
                  v-model="applications"
                  type="checkbox"
                  class="form-check-input"
                  value="App"
                  name="application"
                />
                <label class="form-check-label" for="application-1">App</label>
              </li>
              <li class="form-check">
                <input
                  id="application-2"
                  v-model="applications"
                  type="checkbox"
                  class="form-check-input"
                  value="Website"
                  name="application"
                />
                <label class="form-check-label" for="application-2">Website</label>
              </li>
              <li class="form-check">
                <input
                  id="application-3"
                  v-model="applications"
                  type="checkbox"
                  class="form-check-input"
                  value="Programm"
                  name="application"
                />
                <label class="form-check-label" for="application-3">Programm</label>
              </li>
              <li class="form-check">
                <input
                  id="application-4"
                  v-model="applications"
                  type="checkbox"
                  class="form-check-input"
                  value="Browser-Add-on"
                  name="application"
                />
                <label class="form-check-label" for="application-4">Browser-Add-on</label>
              </li>
            </ul>
          </div>
          <div>
            <h3 class="form-subhead">Betriebssystem:</h3>
            <ul class="list-unstyled">
              <li class="form-check">
                <input
                  id="os-1"
                  v-model="operatingSystems"
                  type="checkbox"
                  class="form-check-input"
                  value="1"
                  name="os"
                />
                <label class="form-check-label" for="os-1">Android</label>
              </li>
              <li class="form-check">
                <input
                  id="os-2"
                  v-model="operatingSystems"
                  type="checkbox"
                  class="form-check-input"
                  value="7"
                  name="os"
                />
                <label class="form-check-label" for="os-2">BlackBerry OS</label>
              </li>
              <li class="form-check">
                <input
                  id="os-3"
                  v-model="operatingSystems"
                  type="checkbox"
                  class="form-check-input"
                  value="2"
                  name="os"
                />
                <label class="form-check-label" for="os-3">iOS</label>
              </li>
              <li class="form-check">
                <input
                  id="os-4"
                  v-model="operatingSystems"
                  type="checkbox"
                  class="form-check-input"
                  value="5"
                  name="os"
                />
                <label class="form-check-label" for="os-4">Linux</label>
              </li>
              <li class="form-check">
                <input
                  id="os-5"
                  v-model="operatingSystems"
                  type="checkbox"
                  class="form-check-input"
                  value="3"
                  name="os"
                />
                <label class="form-check-label" for="os-5">macOS</label>
              </li>
              <li class="form-check">
                <input
                  id="os-6"
                  v-model="operatingSystems"
                  type="checkbox"
                  class="form-check-input"
                  value="4"
                  name="os"
                />
                <label class="form-check-label" for="os-6">Windows</label>
              </li>
              <li class="form-check">
                <input
                  id="os-7"
                  v-model="operatingSystems"
                  type="checkbox"
                  class="form-check-input"
                  value="6"
                  name="os"
                />
                <label class="form-check-label" for="os-7">Windows Phone</label>
              </li>
            </ul>
          </div>

          <div>
            <h3 class="form-subhead">Kostenpflichtig</h3>
            <select id="withCosts" v-model="withCosts" name="withCosts" class="form-control" @change="updateContents">
              <option value="" selected>--------</option>
              <option value="0" selected>Nein</option>
              <option value="1" selected>Ja</option>
            </select>
          </div>
        </form>
        <div class="text-center">
          <button
            class="button button--primary d-lg-none"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#filterForm"
            aria-expanded="false"
            aria-controls="filterForm"
            @click="mobileFilterExpanded = !mobileFilterExpanded"
          >
            {{ mobileFilterToggle }} <span class="fas" :class="mobileFilterExpanded ? 'fa-chevron-circle-up' : 'fa-chevron-circle-down'" />
          </button>
        </div>
      </div>
    </div>
    <div class="col col-12 col-lg-7 col-xl-8">
      <div v-show="activePotentials.length" v-if="dltFeaturesEnabled" class="section-info mb-5">
        <div ref="potentialSlider" class="js-potential-slider potential-slider">
          <div
            v-for="(potential, index) in potentialFilter"
            :key="index"
            ref="potentialSlides"
            class="js-potential-slide"
            :data-ref="potential.value"
          >
            <div class="row">
              <div class="col-12">
                <h1 class="d-none d-lg-block text-center mb-5" v-text="potential.name" />
              </div>
              <div class="col-lg-12 col-xl-7 mb-4" v-html="windowCom['potentialVideo' + potential.value]" />
              <div class="col-lg-12 col-xl-5">
                <p class="mb-5 d-none d-lg-block mt-3" v-html="potential.description" />
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-if="contents.length > 0 || loading" class="row">
        <div v-for="(content, index) in contents" :key="index" class="col col-12 col-xl-6 mb-4">
          <ContentTeaser :content="content" />
        </div>
        <AppPagination
          v-model:pagination="pagination"
          v-model:current-page="currentPage"
          @jump-to="jumpTo"
          @next-page="nextPage"
          @previous-page="previousPage"
        />
      </div>
      <div v-else class="row">
        <div class="col">
          <h2>Ihre Suchanfrage ergab keine Treffer.</h2>
          <p>
            Bitte versuchen Sie es mit anderen Suchbegriffen oder schauen Sie gern auf anderen Datenbanken für freie
            Unterrichtsmaterialien wie
            <a href="https://oerhoernchen.de/suche" target="_blank" rel="noopener noreferrer">OERhörchen</a>.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, ref, watch, watchEffect } from 'vue';

import AppPagination from '../components/AppPagination.vue';
import ContentTeaser from '../components/ContentTeaser.vue';
import { useContentFilter } from '../composables/contentFilter';
import { usePagination } from '../composables/pagination';
import { usePreventEnter } from '../composables/preventEnter';

//  --------------------------------------------------------------------------------------------------------------------
//  component variables
//  --------------------------------------------------------------------------------------------------------------------
const {
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
} = useContentFilter();
const { jumpTo, nextPage, pagination, previousPage } = usePagination(updateContents, currentResponse);
const { preventEnter } = usePreventEnter();

const applications = ref(initArray(queryParams.value.applications));
const subject = ref(queryParams.value.subject || null);
const toolFunctions = ref(initArray(queryParams.value.toolFunctions));
const potentials = ref(initArray(queryParams.value.potentials));
const operatingSystems = ref(initArray(queryParams.value.operatingSystems));
const dataPrivacy = ref(queryParams.value.dataPrivacy || null);
const withCosts = ref(queryParams.value.withCosts || null);
const slider = ref(queryParams.value.slider || null);
const favorites = ref(queryParams.value.favorites || false);

const potentialSlider = ref();
const potentialSlides = ref();

dataUrl.value = '/api/tools';
sorting.value = 'privacy';

//  --------------------------------------------------------------------------------------------------------------------
//  computed
//  --------------------------------------------------------------------------------------------------------------------
const windowCom = computed(() => {
  return window;
});

//  ----------------------------------------------------------------------------
//  TODO: check if working
//  ----------------------------------------------------------------------------
const activePotentials = computed(() => {
  return potentials.value
    .map((activePotential) => {
      const pot = potentialFilter.value.find((p) => p.value.toString() === activePotential.toString());
      if (!pot) return;

      return {
        description: pot.description,
        title: pot.name,
        value: pot.value,
        videoEmbed: window['potentialVideo' + pot.value]
      };
    })
    .filter((p) => p);
});

const toolFilterQueryParams = computed(() => {
  const res = {
    applications: applications.value,
    dataPrivacy: dataPrivacy.value,
    operatingSystems: operatingSystems.value,
    potentials: potentials.value,
    subject: subject.value,
    toolFunctions: toolFunctions.value,
    withCosts: withCosts.value
  };
  if (loggedIn.value) {
    res['favorites'] = favorites.value;
  }
  return res;
});

const dltFeaturesEnabled = computed(() => {
  return window.dltFeatures;
});

const potentialFilter = computed(() => {
  return window.potentialFilter;
});

const dataPrivacyOptions = computed(() => {
  return window.dataPrivacyFilter;
});

const functionsFilter = computed(() => {
  return window.functionsFilter;
});

//  --------------------------------------------------------------------------------------------------------------------
//  watchers
//  --------------------------------------------------------------------------------------------------------------------
watchEffect(() => {
  queryParams.value = toolFilterQueryParams.value;
});

watch([toolFunctions, applications, operatingSystems, potentials], () => {
  debouncedUpdate();
});

watch(activePotentials, () => {
  nextTick(() => {
    const activeValues = activePotentials.value.map((p) => p.value.toString());

    if (!slider.value) {
      console.log('slider inited');
      // eslint-disable-next-line no-undef
      slider.value = $(potentialSlider.value).slick();
    }

    slider.value.slick('refresh');
    slider.value.slick('slickUnfilter');
    slider.value.slick('slickFilter', (s) => {
      return activeValues.includes(potentialSlides.value[s].dataset.ref);
    });
  });
});

//  --------------------------------------------------------------------------------------------------------------------
//  lifecycle
//  --------------------------------------------------------------------------------------------------------------------
updateContents();
</script>

<style scoped></style>
