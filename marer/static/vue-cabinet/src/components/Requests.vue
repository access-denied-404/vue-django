<template>
    <div class="container">
      <div class="row">
      <h1 class="text-center">Заявка №{{issue.id}}</h1>
      </div>

      <div class="row">
        <div class="col-md-3">
          <div class="visible-md visible-lg container" data-spy="affix">
            <div class="row">
              <div class="col-md-3">
                <div class="panel panel-default">
                  <div class="list-group">
                    <a class="list-group-item" :href="'#/cabinet/issues/' + issue.id">Сведения о заявлении</a>
                    <a class="list-group-item" :href="'#/cabinet/issues/' + issue.id + '/requests'">Запросы и обсуждения</a>
                  </div>
                </div>
                <div style="margin-top: 30px;">
                  <a href="#/cabinet/issues" style="margin-left: 15px;">Вернуться в личный кабинет</a>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-9">
          <div class="panel panel-info">
            <div class="panel-heading">Документы</div>
            <div class="panel-body">
              <div class="row">
                <div class="col-md-12">
                  <form method="post" enctype="multipart/form-data">
                    <table class="table table-condensed">
                      <tbody>
                        <tr><td><a :href="issue.bg_doc.file">Проект</a></td></tr>
                        <tr><td><a :href="issue.transfer_acceptance_act.file">Акт</a></td></tr>
                        <tr v-if="issue.contract_of_guarantee"><td><a :href="issue.contract_of_guarantee.file">Согласие на взаимодействие с БКИ (поручителя)</a></td></tr>
                        <!--<tr><td><a href="/documents/approval_and_change_sheet.docx" download="Лист_согласования_и_изменения_БГ.docx">Лист согласования и изменения БГ</a></td></tr>-->
                      </tbody>
                    </table>
                  </form>
                </div>
              </div>
            </div>
          </div>
          <form method="post" enctype="multipart/form-data">
            <div class="panel panel-info">
              <div class="panel-heading">Новое сообщение</div>
              <div class="panel-body">
                <div class="container-fluid">
                  <div class="row">
                    <div class="col-md-5">
                      <label for="tarea" class="text-center">Сообщение</label>
                      <textarea id="tarea" rows="4" cols="50"></textarea>
                    </div>
                    <div class="col-md-7">
                      <div class="text-center"><span class="h5">Прикрепить документы</span></div>
                      <table class="table table-condensed">
                        <tr><td class="h5"><small><input type="file"/></small></td><td class="h5"><small><input type="file"/></small></td></tr>
                        <tr><td class="h5"><small><input type="file"/></small></td><td class="h5"><small><input type="file"/></small></td></tr>
                        <tr><td class="h5"><small><input type="file"/></small></td><td class="h5"><small><input type="file"/></small></td></tr>
                      </table>
                    </div>
                  </div>
                  <div class="row text-center">
                      <button type="submit" name="action" value="send_msg" class="btn btn-primary">Отправить</button>
                    </div>
                </div>
              </div>
            </div>
          </form>
          <!--<div v-for="msg in issue.clarification_messages.all" class="panel panel-info">-->
            <!--<div class="panel-body">-->
              <!--<div class="container-fluid">-->
                <!--<div class="row">-->
                  <!--<div class="col-md-4">-->
                    <!--<span class="h3">{{ msg.user.get_full_name }}</span>-->
                    <!--<div class="h4">{{msg.created_at}}</div>-->
                  <!--</div>-->
                  <!--<div class="col-md-8">-->
                    <!--<div>{{msg.message}}</div>-->
                  <!--</div>-->
                <!--</div>-->
              <!--</div>-->
            <!--</div>-->
          <!--</div>-->
        </div>
      </div>

    </div>
</template>

<script>
  import jQuery from 'jquery'
  import moment from 'moment'
  import {input, checkbox, select} from 'vue-strap'
  import DateTimePicker from 'vue-bootstrap-datetimepicker'
  import BS3SelectField from '@/components/inputs/BS3SelectField'
  import BS3RadioField from '@/components/inputs/BS3RadioField'
  import 'eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.css'
  import {Money} from 'v-money'

  moment.locale = 'ru'
  let dateformat = 'DD.MM.YYYY'

  export default {
    name: 'issue',
    components: {
      'bs-select': select,
      'bs-input': input,
      'checkbox': checkbox,
      'bs3-select-field': BS3SelectField,
      'bs3-radio-field': BS3RadioField,
      'date-time-picker': DateTimePicker,
      'Money': Money
    },
    props: ['id'],
    data () {
      return {
        api_url: window.debug ? 'http://localhost:8000/rest/issue/' : '/rest/issue/',
        issue: {}
      }
    },
    mounted: function () {
      jQuery.getJSON(this.api_url + this.$route.params.id + '?format=json', (data, status, xhr) => {
        this.update_form_data(data)
      })
    },
    computed: {
      date_range: {
        get () {
          if (this.issue.bg_end_date) {
            let val
            let start = moment(this.issue.bg_start_date, dateformat)
            let end = this.issue.bg_end_date
            val = 1 + (end.year() - start.year()) * 12 + end.month() - start.month()
            if (isNaN(val)) {
              return ''
            } else {
              return val
            }
          }
          return ''
        },
        set () {
        }
      }
    },
    methods: {
      update_form_data: function (data) {
        data.csrfmiddlewaretoken = this.$cookie.get('csrftoken')
        this.issue = data
        this.issue.bg_doc = data.bg_doc
        this.issue.transfer_acceptance_act = data.transfer_acceptance_act
        this.contract_of_guarantee = data.contract_of_guarantee
      },
      save_issue: function () {
        jQuery.post(this.api_url + this.$route.params.id, this.issue, (data, status, xhr) => {
          this.update_form_data(data)
        })
      }
    }
  }
</script>
