// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'

Vue.config.productionTip = false

var products = JSON.parse(document.getElementById('app').getAttribute('products'))
var dadataToken = document.getElementById('app').getAttribute('dadata_token')
var issueID = document.getElementById('app').getAttribute('issue-id')
window.regdata = document.getElementById('app').getAttribute('regdata')

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  data: {
    csrf: document.getElementById('app').getAttribute('csrf'),
    products: products,
    token: dadataToken,
    issue_id: issueID
  },
  template: '<App :csrf="csrf" :products="products" :token="token" :issue_id="issue_id" />',
  components: { App }
})
