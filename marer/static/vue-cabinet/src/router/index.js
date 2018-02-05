import Vue from 'vue'
import Router from 'vue-router'
import Cabinet from '@/components/Cabinet'
import CabinetIssues from '@/components/CabinetIssues'
import CabinetProfile from '@/components/CabinetProfile'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      redirect: '/cabinet/issues'
    },
    {
      path: '/cabinet',
      name: 'cabinet',
      component: Cabinet,
      redirect: '/cabinet/issues',
      children: [
        {
          path: 'issues',
          name: 'issues',
          component: CabinetIssues
        },
        {
          path: 'profile',
          name: 'profile',
          component: CabinetProfile
        }
      ]
    }
  ]
})
