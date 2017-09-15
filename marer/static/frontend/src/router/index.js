import Vue from 'vue'
import Router from 'vue-router'
import Hello from '@/components/Hello'
import FormBankGuarantee from '@/components/FormBankGuarantee'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Hello',
      component: Hello
    },
    {
      path: '/BankGuaranteeProduct',
      name: 'FormBankGuarantee',
      component: FormBankGuarantee
    }
  ]
})
