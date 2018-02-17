<template>
  <div class="col-md-3">
    <div class="visible-md visible-lg container" data-spy="affix">
      <div class="row">
        <div class="col-md-3">
          <div class="panel panel-default">
            <div class="list-group">
              <a class="list-group-item" :href="'#/cabinet/issues/' + this.id + '/info'" v-bind:class="{'active': this.$route.name === 'issue-info'}">Сведения о заявлении</a>
              <a class="list-group-item" :href="'#/cabinet/issues/' + this.id + '/survey'" v-bind:class="{'active': this.$route.name === 'issue-survey'}">Анкета</a>
              <a class="list-group-item" :href="'#/cabinet/issues/' + this.id + '/documents'" v-bind:class="{'active': this.$route.name === 'issue-documents'}">Пакет документов</a>
              <a class="list-group-item" :href="'#/cabinet/issues/' + this.id + '/security-mgmt'" v-bind:class="{'active': this.$route.name === 'issue-security-mgmt'}">Департамент безопасности</a>
              <a class="list-group-item" :href="'#/cabinet/issues/' + this.id + '/lawyers-mgmt'" v-bind:class="{'active': this.$route.name === 'issue-lawyers-mgmt'}">Правовое управление</a>
              <a class="list-group-item" :href="'#/cabinet/issues/' + this.id + '/doc-ops-mgmt'" v-bind:class="{'active': this.$route.name === 'issue-doc-ops-mgmt'}">Управление развития ДО</a>
              <a class="list-group-item" :href="'#/cabinet/issues/' + this.id + '/messaging'" v-bind:class="{'active': this.$route.name === 'issue-messaging'}">Обсуждения</a>
            </div>
          </div>
          <div style="margin-top: 30px;">
            <a href="#/cabinet/issues" style="margin-left: 15px;">Вернуться в личный кабинет</a>
          </div>
        </div>
      </div>
    </div>
    <div class="visible-sm visible-xs">
      <div class="h4 text-center text-primary">Этапы прохождения заявки</div>
      <div class="panel panel-default">
        <div class="list-group">
          <a class="list-group-item" :href="'#/cabinet/issues/' + this.id + '/info'" v-bind:class="{'active': this.$route.name === 'issue-info'}">Сведения о заявлении</a>
          <a class="list-group-item" :href="'#/cabinet/issues/' + this.id + '/survey'" v-bind:class="{'active': this.$route.name === 'issue-survey'}">Анкета</a>
          <a class="list-group-item" :href="'#/cabinet/issues/' + this.id + '/documents'" v-bind:class="{'active': this.$route.name === 'issue-documents'}">Пакет документов</a>
          <a class="list-group-item" :href="'#/cabinet/issues/' + this.id + '/security-mgmt'" v-bind:class="{'active': this.$route.name === 'issue-security-mgmt'}">Департамент безопасности</a>
          <a class="list-group-item" :href="'#/cabinet/issues/' + this.id + '/lawyers-mgmt'" v-bind:class="{'active': this.$route.name === 'issue-lawyers-mgmt'}">Правовое управление</a>
          <a class="list-group-item" :href="'#/cabinet/issues/' + this.id + '/doc-ops-mgmt'" v-bind:class="{'active': this.$route.name === 'issue-doc-ops-mgmt'}">Управление развития ДО</a>
          <a class="list-group-item" :href="'#/cabinet/issues/' + this.id + '/messaging'" v-bind:class="{'active': this.$route.name === 'issue-messaging'}">Обсуждения</a>
        </div>
      </div>
      <div style="margin-top: 30px;">
        <a href="#/cabinet/issues" style="margin-left: 15px;">Вернуться в личный кабинет</a>
      </div>
    </div>
  </div>
</template>

<script>
  import jQuery from 'jquery'
  import _ from 'lodash'

  export default {
    name: 'issue',
    props: ['id'],
    data () {
      return {
        issue: {}
      }
    },
    watch: {
      id: _.debounce(function () {
        let apiUrl = window.debug ? 'http://localhost:8000/rest/issue/' : '/rest/issue/'
        jQuery.getJSON(apiUrl + this.$props.id + '?format=json', (data, status, xhr) => {
          this.issue = data
        })
      }, 250)
    }
  }
</script>
