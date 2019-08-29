export const preventEnter = {
  methods: {
    preventEnter (event) {
      if(event.keyCode === 13) {
        event.preventDefault();
        return false;
      }
    }
  }
}
