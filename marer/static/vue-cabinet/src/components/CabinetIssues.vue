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
          <tr v-for="issue in issues">
            <td v-if="issue.status === 'review'" class="bg-info"><a :href="'#/cabinet/issues/'+issue.id">{{issue.id}}</a></td>
            <td v-if="issue.status === 'registering'" class="bg-warning"><a :href="'#/cabinet/issues/'+issue.id">{{issue.id}}</a></td>
            <td v-if="issue.status === 'cancelled'" class="bg-danger"><a :href="'#/cabinet/issues/'+issue.id">{{issue.id}}</a></td>
            <td v-if="issue.status === 'finished'" class="bg-success"><a :href="'#/cabinet/issues/'+issue.id">{{issue.id}}</a></td>

            <td v-if="issue.status === 'review'" class="bg-info"></td>
            <td v-if="issue.status === 'registering'" class="bg-warning"></td>
            <td v-if="issue.status === 'cancelled'" class="bg-danger"></td>
            <td v-if="issue.status === 'finished'" class="bg-success"></td>

            <td v-if="issue.status === 'review'" class="bg-info">{{issue.issuer_short_name}}</td>
            <td v-if="issue.status === 'registering'" class="bg-warning">{{issue.issuer_short_name}}</td>
            <td v-if="issue.status === 'cancelled'" class="bg-danger">{{issue.issuer_short_name}}</td>
            <td v-if="issue.status === 'finished'" class="bg-success">{{issue.issuer_short_name}}</td>

            <td v-if="issue.status === 'review'" class="bg-info">{{issue.bg_sum}}</td>
            <td v-if="issue.status === 'registering'" class="bg-warning">{{issue.bg_sum}}</td>
            <td v-if="issue.status === 'cancelled'" class="bg-danger">{{issue.bg_sum}}</td>
            <td v-if="issue.status === 'finished'" class="bg-success">{{issue.bg_sum}}</td>

            <td v-if="issue.status === 'review'" class="bg-info"></td>
            <td v-if="issue.status === 'registering'" class="bg-warning"></td>
            <td v-if="issue.status === 'cancelled'" class="bg-danger"></td>
            <td v-if="issue.status === 'finished'" class="bg-success"></td>

            <td v-if="issue.status === 'review'" class="bg-info"></td>
            <td v-if="issue.status === 'registering'" class="bg-warning"></td>
            <td v-if="issue.status === 'cancelled'" class="bg-danger"></td>
            <td v-if="issue.status === 'finished'" class="bg-success"></td>

            <td v-if="issue.status === 'review'" class="bg-info"></td>
            <td v-if="issue.status === 'registering'" class="bg-warning"></td>
            <td v-if="issue.status === 'cancelled'" class="bg-danger"></td>
            <td v-if="issue.status === 'finished'" class="bg-success"></td>
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
    }
  }
</script>
