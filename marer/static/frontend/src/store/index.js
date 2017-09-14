import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

const debug = process.env.NODE_ENV !== 'production'

export default new Vuex.Store({
  strict: debug,
  state: {
    count: 1
  },
  mutations: {
    increment (state, payload) {
      state.count += payload.counter
    }
  }
})
