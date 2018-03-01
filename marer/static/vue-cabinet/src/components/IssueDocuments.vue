<template>
  <div class="container">
    <div class="row">
      <h1 class="text-center">Заявка №{{issue.id}}</h1>
      <!--<div class="h4 text-center"><b>Банковская гарантия</b>-->
      <!--на сумму <b>16 000,00 руб.</b>-->
      <!--</div>-->
    </div>
    <div class="row">
      <issue-menu :id="this.issue.id"></issue-menu>

      <div class="col-md-9">
        <div class="well well-sm text-center">
          Ссылка для подписания заявления клиентом:
          <strong>
          http://sgbgarant.ru/cabinet/requests/{{issue.id}}/rsd
          </strong>
          <a class="btn btn-link btn-xs" :href="'http://sgbgarant.ru/cabinet/requests/' + issue.id + '/rsd'" target="_blank">
            <span class="glyphicon glyphicon-new-window"></span>
          </a>
        </div>

        <div class="row">
          <div class="col-md-12">
            <div class="panel panel-info">
              <div class="panel-heading">Документы</div>
              <div class="panel-body">
                <div class="row">
                  <div class="col-md-12">
                    <table class="table table-condensed">
                      <tr class="application_doc" v-if="issue.application_doc">
                        <td class="h6">
                          <a :href="issue.application_doc.file">
                            <b>Заявление на предоставление банковской гарантии</b>
                          </a>
                        </td>
                      </tr>
                      <tr v-if="finance_documents">
                        <td>
                          <h4 style="font-weight: bold;">Финансовые документы</h4>
                        </td>
                      </tr>
                      <tr v-for="(doc, index) in finance_documents">
                          <td :id="'fin-doc-' + doc.id" v-show="doc.visible">
                              <div class="row">
                                  <div class="col-md-9">
                                      <a v-if="doc.document" :href="doc.document.file" v-text="doc.name"></a>
                                      <div v-else v-text="doc.name"></div>
                                  </div>

                                  <div class="col-md-3">
                                      <div class="row">
                                          <div v-if="doc.document" class="col-md-8">
                                              <label :for="'upload_doc_' + doc.id">
                                                <span class="glyphicon glyphicon-upload text-primary" role="button"> Загрузить</span>
                                                <input type="file" :id="'upload_doc_' + doc.id" class="hidden"/>
                                              </label>
                                          </div>
                                          <div v-else class="col-md-8">
                                              <label>
                                                <span class="glyphicon glyphicon-upload text-primary" role="button"> Загрузить</span>
                                                <input type="file" class="hidden"/>
                                              </label>
                                          </div>
                                          <div v-if="doc.document && doc.document.sign_state" class="col-md-1">
                                              <span v-if="doc.document.sign_state == 'verified'"
                                                    class="glyphicon glyphicon-ok-circle text-success">

                                              </span>
                                              <span v-else-if="doc.document.sign_state == 'corrupted'"
                                                    class="glyphicon glyphicon glyphicon-ban-circle text-danger">

                                              </span>
                                              <span v-else class="glyphicon glyphicon glyphicon-remove-circle"></span>
                                          </div>
                                          <div v-if="doc.document" class="col-md-1">
                                              <a href="#"><span class="glyphicon glyphicon-remove text-danger"></span></a>
                                          </div>
                                      </div>
                                  </div>
                            </div>
                          </td>
                      </tr>
                      <tr v-if="finance_documents">
                          <a class="btn btn-primary btn-sm pull-right"
                             :href="'issue/' + issue.id + '/docs-zip?group=2'"
                             target="_blank">Скачать архив
                          </a>
                      </tr>
                      <tr v-if="legal_documents">
                        <td>
                          <h4 style="font-weight: bold;">Юридические документы</h4>
                        </td>
                      </tr>
                      <tr v-for="(doc, index) in legal_documents">
                        <td :id="'jur-doc-' + doc.id" v-show="doc.visible">
                            <div class="row">
                                  <div class="col-md-9">
                                      <a v-if="doc.document" :href="doc.document.file" v-text="doc.name"></a>
                                      <div v-else v-text="doc.name"></div>
                                  </div>

                                  <div class="col-md-3">
                                      <div class="row">
                                          <div v-if="doc.document" class="col-md-8">
                                              <label :for="'upload_doc_' + doc.id">
                                                <span class="glyphicon glyphicon-upload text-primary" role="button"> Загрузить</span>
                                                <input type="file" :id="'upload_doc_' + doc.id" class="hidden"/>
                                              </label>
                                          </div>
                                          <div v-else class="col-md-8">
                                              <label>
                                                <span class="glyphicon glyphicon-upload text-primary" role="button"> Загрузить</span>
                                                <input type="file" class="hidden"/>
                                              </label>
                                          </div>
                                          <div v-if="doc.document && doc.document.sign_state" class="col-md-1">
                                              <span v-if="doc.document.sign_state == 'verified'"
                                                    class="glyphicon glyphicon-ok-circle text-success">

                                              </span>
                                              <span v-else-if="doc.document.sign_state == 'corrupted'"
                                                    class="glyphicon glyphicon glyphicon-ban-circle text-danger">

                                              </span>
                                              <span v-else class="glyphicon glyphicon glyphicon-remove-circle"></span>
                                          </div>
                                          <div v-if="doc.document" class="col-md-1">
                                              <a href="#"><span class="glyphicon glyphicon-remove text-danger"></span></a>
                                          </div>
                                      </div>
                                  </div>
                            </div>
                        </td>
                      </tr>
                      <tr v-if="legal_documents">
                          <a class="btn btn-primary btn-sm pull-right"
                             :href="'issue/' + issue.id + '/docs-zip?group=1'"
                             target="_blank">Скачать архив
                          </a>
                      </tr>
                      <tr v-if="other_documents">
                        <td>
                          <h4 style="font-weight: bold;">Прочее</h4>
                        </td>
                      </tr>
                      <tr v-for="(doc, index) in other_documents">
                        <td :id="'oth-doc-' + doc.id" v-show="doc.visible">
                            <div class="row">
                                  <div class="col-md-9">
                                      <a v-if="doc.document" :href="doc.document.file" v-text="doc.name"></a>
                                      <div v-else v-text="doc.name"></div>
                                  </div>

                                  <div class="col-md-3">
                                      <div class="row">
                                          <div v-if="doc.document" class="col-md-8">
                                              <label :for="'upload_doc_' + doc.id">
                                                <span class="glyphicon glyphicon-upload text-primary" role="button"> Загрузить</span>
                                                <input type="file" :id="'upload_doc_' + doc.id" class="hidden"/>
                                              </label>
                                          </div>
                                          <div v-else class="col-md-8">
                                              <label>
                                                <span class="glyphicon glyphicon-upload text-primary" role="button"> Загрузить</span>
                                                <input type="file" class="hidden"/>
                                              </label>
                                          </div>
                                          <div v-if="doc.document && doc.document.sign_state" class="col-md-1">
                                              <span v-if="doc.document.sign_state == 'verified'"
                                                    class="glyphicon glyphicon-ok-circle text-success">

                                              </span>
                                              <span v-else-if="doc.document.sign_state == 'corrupted'"
                                                    class="glyphicon glyphicon glyphicon-ban-circle text-danger">

                                              </span>
                                              <span v-else class="glyphicon glyphicon glyphicon-remove-circle"></span>
                                          </div>
                                          <div v-if="doc.document" class="col-md-1">
                                              <a href="#"><span class="glyphicon glyphicon-remove text-danger"></span></a>
                                          </div>
                                      </div>
                                  </div>
                            </div>
                        </td>
                      </tr>
                      <tr v-if="other_documents">
                          <a class="btn btn-primary btn-sm pull-right"
                             :href="'issue/' + issue.id + '/docs-zip?group=3'"
                             target="_blank">Скачать архив
                          </a>
                      </tr>
                      <tr v-if="issue.propose_documents_app">
                          <td>
                              <h4 style="font-weight: bold">Договора и акты</h4>
                          </td>
                      </tr>
                      <tr v-for="(doc, index) in issue.propose_documents_app">
                        <td :id="'oth-doc-' + doc.id" v-show="doc.visible">
                            <div class="row">
                                  <div class="col-md-9">
                                      <a v-if="doc.document" :href="doc.document.file" v-text="doc.name"></a>
                                      <div v-else v-text="doc.name"></div>
                                  </div>

                                  <div class="col-md-3">
                                      <div class="row">
                                          <div v-if="doc.document" class="col-md-8">
                                              <label :for="'upload_doc_' + doc.id">
                                                <span class="glyphicon glyphicon-upload text-primary" role="button"> Загрузить</span>
                                                <input type="file" :id="'upload_doc_' + doc.id" class="hidden"/>
                                              </label>
                                          </div>
                                          <div v-else class="col-md-8">
                                              <label>
                                                <span class="glyphicon glyphicon-upload text-primary" role="button"> Загрузить</span>
                                                <input type="file" class="hidden"/>
                                              </label>
                                          </div>
                                          <div v-if="doc.document && doc.document.sign_state" class="col-md-1">
                                              <span v-if="doc.document.sign_state == 'verified'"
                                                    class="glyphicon glyphicon-ok-circle text-success">

                                              </span>
                                              <span v-else-if="doc.document.sign_state == 'corrupted'"
                                                    class="glyphicon glyphicon glyphicon-ban-circle text-danger">

                                              </span>
                                              <span v-else class="glyphicon glyphicon glyphicon-remove-circle"></span>
                                          </div>
                                          <div v-if="doc.document" class="col-md-1">
                                              <a href="#"><span class="glyphicon glyphicon-remove text-danger"></span></a>
                                          </div>
                                      </div>
                                  </div>
                            </div>
                        </td>
                      </tr>
                      <tr v-if="issue.propose_documents_app">
                          <a class="btn btn-primary btn-sm pull-right"
                             :href="'issue/' + issue.id + '/docs-zip?group=4'"
                             target="_blank">Скачать архив
                          </a>
                      </tr>
                    </table>

                  </div>
            </div>
        </div>
            </div>
          </div>
        </div>

        <div class="row">
          <div class="col-md-12 text-center">
            <button class="btn btn-primary" type="button" v-on:click="save_issue">Сохранить</button>
          </div>
        </div>
      </div>
    </div>
    <br/>
  </div>
</template>

<script>
  import jQuery from 'jquery'
  import moment from 'moment'
  import {input, checkbox, select} from 'vue-strap'
  import DateTimePicker from 'vue-bootstrap-datetimepicker'
  import BS3SelectField from '@/components/inputs/BS3SelectField'
  import BS3RadioField from '@/components/inputs/BS3RadioField'
  import IssueMenu from '@/components/IssueMenu'
  import 'eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.css'
  import {Money} from 'v-money'
  import axios from 'axios'

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
      'Money': Money,
      'issue-menu': IssueMenu
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
      update_form_data (data) {
        this.issue = data
        this.issue.bg_start_date = moment(data.bg_start_date, dateformat)
        this.issue.bg_end_date = moment(data.bg_end_date, dateformat)

        this.finance_documents = jQuery.grep(data.propose_documents, function (n, i) {
          return n.type === 2
        })
        this.legal_documents = jQuery.grep(data.propose_documents, function (n, i) {
          return n.type === 1
        })
        this.other_documents = jQuery.grep(data.propose_documents, function (n, i) {
          return n.type === 3
        })
      },
      save_issue () {
        axios.post(this.api_url + this.$route.params.id, {
          body: this.issue
        }).then(response => {
          this.update_form_data(response.data)
        })
      }
    }
  }
</script>
