
import axios from 'axios'

export const axiosMixin = {
  methods: {
    getAxiosInstance () {
      const axiosInstance = axios.create({
        headers: {
          'X-CSRFToken': window.dllData.csrfToken
        }
      })
      return axiosInstance
    }
  }
}