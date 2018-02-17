<template>
  <div class="col-md-3">
    <div class="visible-md visible-lg container" data-spy="affix">
      <div class="row">
        <div class="col-md-3">
          <div class="panel panel-default">
            <div class="list-group">
              <a class="list-group-item" :href="'#/cabinet/issues/' + this.id">Сведения о заявлении</a>
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
          <a class="list-group-item" :href="'#/cabinet/issues/' + this.id">Сведения о заявлении</a>
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
