// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'

Vue.config.productionTip = false

var products = JSON.parse(document.getElementById('app').getAttribute('products'))
window.regdata = document.getElementById('app').getAttribute('regdata')

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  data: {
    csrf: document.getElementById('app').getAttribute('csrf'),
    products: products
  },
  template: '<App :csrf="csrf" :products="products"/>',
  components: { App }
})
