import Vue from 'vue'
import Router from 'vue-router'
import Stub from '@/components/Stub'
import FormBankGuarantee from '@/components/FormBankGuarantee'
import FormCredit from '@/components/FormCredit'

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
      path: '/LeasingProduct',
      name: 'LeasingProduct',
      component: Stub
    }
  ]
})
