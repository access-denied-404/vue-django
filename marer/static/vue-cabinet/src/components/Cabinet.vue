<template>
  <div class="container container-bgnd">
    <div class="row">
      <div class="col-sm-3 col-md-2 sidebar">
        <div class="list-group">
          <a href="#/cabinet/issues" class="list-group-item" v-bind:class="{active: isIssuesActive}">Заявки</a>
          <!--<a href="/cabinet/organizations" class="list-group-item">Организации</a>-->
          <a href="#/cabinet/profile" class="list-group-item" v-bind:class="{active: isProfileActive}">Профиль</a>
        </div>
      </div>
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'cabinet',
    data () {
      return {
      }
    },
    computed: {
      isIssuesActive: function () {
        return this.$route.name === 'issues'
      },
      isProfileActive: function () {
        return this.$route.name === 'profile'
      }
    }
  }
</script>
