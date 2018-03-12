<template>
  <div class="col-sm-9 col-md-10">
    <div class="clearfix"></div>
    <br/>
    <div class="panel panel-info">
      <table class="table">
        <tbody>
          <tr class="bg-info">
            <th class="h6">Номер</th>
            <th class="h6">Дата заведения заявки</th>
            <th class="h6">Организация</th>
            <th class="h6">ИНН принципала</th>
            <th class="h6">Сумма</th>
            <th class="h6">Статус</th>
            <th class="h6">Агент</th>
            <th></th>
          </tr>
          <tr v-for="issue in issues"
          v-bind:class="{
              'bg-warning': isRegistering(issue.status),
              'bg-danger': isCancelled(issue.status),
              'bg-success': isFinished(issue.status) }">
            <td><a :href="'#/cabinet/issues/'+issue.id" v-text=issue.id></a></td>
            <td v-text=createdAt(issue.created_at)></td>
            <td v-text=issue.issuer_short_name></td>
            <td v-text=issue.issuer_inn></td>
            <td v-text=formatSum(issue.bg_sum)></td>
            <td v-if=isRegistering(issue.status)>Оформление заявки</td>
            <td v-if=isCancelled(issue.status)>Отменена</td>
            <td v-if=isFinished(issue.status)>Завершена</td>
            <td v-if=isReviewing(issue.status)>Рассмотрение заявки</td>
            <td v-text=issue.user.legal_name></td>
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
      },
      isReviewing: function (status) {
        if (status === 'review') {
          return true
        } else {
          return false
        }
      },
      createdAt: function (createdDate) {
        var year = createdDate.slice(0, 4)
        var month = createdDate.slice(5, 7)
        var day = createdDate.slice(8, 10)
        var time = createdDate.slice(11, 19)
        var date = day + '.' + month + '.' + year + ' ' + time
        return date
      },
      formatSum: function (sum) {
        var res = ''

        if (sum.includes('.')) {
          var fractionSum = sum.split('.')[1]
          var integerSum = sum.split('.')[0]
        } else if (sum.includes(',')) {
          fractionSum = sum.split(',')[1]
          integerSum = sum.split(',')[0]
        } else {
          integerSum = sum
          fractionSum = 0
        }
        if (fractionSum === '00') {
          fractionSum = 0
        }
        var splittedListOfIntegerSum = integerSum.split('').reverse().join('').match(/.{1,3}/g)
        for (var group in splittedListOfIntegerSum.reverse()) {
          res += splittedListOfIntegerSum[group].split('').reverse().join('') + ' '
        }
        res = res.trim()
        if (fractionSum !== 0) {
          if (fractionSum[1] !== 0) {
            res += ',' + fractionSum
          } else {
            res += ',' + fractionSum[0]
          }
        }
        return res
      }
    }
  }
</script>
