import Vue from 'vue'
import Router from 'vue-router'
import Stub from '@/components/Stub'
import FormBankGuarantee from '@/components/FormBankGuarantee'
import FormCredit from '@/components/FormCredit'
import FormFactoring from '@/components/FormFactoring'
import FormLeasing from '@/components/FormLeasing'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Stub',
      component: Stub
    },
    {
      path: '/BankGuaranteeProduct',
      name: 'FormBankGuarantee',
      component: FormBankGuarantee
    },
    {
      path: '/CreditProduct',
      name: 'CreditProduct',
      component: FormCredit
    },
    {
      path: '/FactoringProduct',
      name: 'FactoringProduct',
      component: FormFactoring
    },
    {
      path: '/LeasingProduct',
      name: 'LeasingProduct',
      component: FormLeasing
    }
  ]
})
