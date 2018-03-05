<template>
  <div class="container">
    <div class="row">
      <h1 class="text-center">Заявка №{{issue.id}}</h1>
      <div class="h4 text-center"><b>Банковская гарантия</b>
        для <b>{{issue.issuer_short_name}}</b>
        на сумму <b>{{Number(issue.bg_sum).toLocaleString()}} руб.</b>
      </div>
    </div>
    <div class="row">
      <issue-menu :id="this.issue.id"></issue-menu>
      <div class="col-md-9">
        <div class="row">
          <div class="col-md-12">
            <div class="panel panel-info">
              <div class="panel-heading">Заключение департамента безопасности</div>
              <div class="panel-body">
                <div  class="row" style="border-bottom: 1px solid #ccc;padding-bottom: 10px;">
                  <div class="col-md-3"><b>Заключение ДБ</b></div>
                  <div class="col-md-1 text-right">
                    <a v-if="issue.sec_dep_conclusion_doc" :href="issue.sec_dep_conclusion_doc.file" class="btn btn-primary btn-sm" type="button">Скачать</a>
                  </div>
                  <div class="col-md-1 text-right">
                    <input class="btn btn-primary btn-sm" @click="generate_sec_dep_conclusion_doc" type="button" value="Сформировать">
                  </div>
                </div>
                <div class="row">
                  <div class="col-md-12">
                    <checkbox v-model="issue.is_positive_security_department_conclusion" :type="'primary'">
                      Наличие положительного Заключения СБ</checkbox>
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
  import {input, checkbox, select} from 'vue-strap'
  import DateTimePicker from 'vue-bootstrap-datetimepicker'
  import BS3SelectField from '@/components/inputs/BS3SelectField'
  import BS3RadioField from '@/components/inputs/BS3RadioField'
  import IssueMenu from '@/components/IssueMenu'
  import 'eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.css'
  import {Money} from 'v-money'
  import axios from 'axios'

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
        issue: {},
        errors: []
      }
    },
    mounted: function () {
      jQuery.getJSON(this.api_url + this.$route.params.id + '/sec-dep-mgmt?format=json', (data, status, xhr) => {
        this.issue = data
      })
    },
    methods: {
      generate_sec_dep_conclusion_doc () {
        this.errors = []
        axios.post(this.api_url + this.$route.params.id + '/generate_sec-dep-mgmt', {
          body: this.issue
        }).then(response => {
          this.update_form_data(response.data)
        }).catch(error => {
          this.errors = error.response.data.errors
        })
      },
      save_issue () {
        axios.post(this.api_url + this.$route.params.id + '/sec-dep-mgmt?format=json', {
          body: this.issue
        }).then(response => {
          this.update_form_data(response.data)
        })
      }
    }
  }
</script>
