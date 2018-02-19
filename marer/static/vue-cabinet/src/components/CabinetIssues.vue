<template>
  <div class="col-sm-9 col-md-10">
    <div class="clearfix"></div>
    <br/>
    <div class="panel panel-info">
      <table class="table">
        <tbody>
          <tr class="bg-info">
            <th class="h6">Номер</th>
            <th class="h6">Дата<br/>заведения<br/>заявки</th>
            <th class="h6">Организация</th>
            <th class="h6">Сумма</th>
            <th class="h6">Статус</th>
            <th class="h6">Последний<br/>комментарий</th>
            <th></th>
          </tr>
          <tr v-for="issue in issues"
          v-bind:class="{
              'bg-warning': isRegistering(issue.status),
              'bg-danger': isCancelled(issue.status),
              'bg-success': isFinished(issue.status) }">
            <td><a :href="'#/cabinet/issues/'+issue.id">{{issue.id}}</a></td>
            <td></td>
            <td>{{issue.issuer_short_name}}</td>
            <td>{{issue.bg_sum}}</td>
            <td></td>
            <td></td>
            <td></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
  import jQuery from 'jquery'
  export default {
    name: 'issues',
    data () {
      return {
        issues: []
      }
    },
    mounted: function () {
      jQuery.getJSON('/rest/issues?format=json', (data, status, xhr) => {
        this.issues = data
      })
    },
    methods: {
      isRegistering: function (status) {
        if (status === 'registering') {
          return true
        } else {
          return false
        }
      },
      isCancelled: function (status) {
        if (status === 'cancelled') {
          return true
        } else {
          return false
        }
      },
      isFinished: function (status) {
        if (status === 'finished') {
          return true
        } else {
          return false
        }
      }
    }
  }
</script>
