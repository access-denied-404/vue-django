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
        <div class="row">
          <div class="col-md-12">
            <div class="panel panel-info">
              <div class="panel-heading">Заключение правового управления</div>
              <div class="panel-body">
                <div  class="row" style="border-bottom: 1px solid #ccc;padding-bottom: 10px;">
                  <div class="col-md-12">
                    <div class="alert alert-danger" v-if="this.errors.length > 0">
                      <p v-for="err in this.errors" class="text-center">
                        <span class="h2">{{ err }}</span>
                      </p>
                    </div>
                  </div>
                  <div class="col-md-3"><b>Заключение ПУ</b></div>
                  <div class="col-md-1 text-right">
                    <a v-if="issue.lawyers_dep_conclusion_doc" :href="issue.lawyers_dep_conclusion_doc.file" class="btn btn-primary btn-sm" type="button">Скачать</a>
                  </div>
                  <div class="col-md-1 text-right">
                    <input class="btn btn-primary btn-sm" type="button" @click="generate_lawyers_dep_conclusion_doc" value="Сформировать">
                  </div>
                </div>
                <div class="row">
                  <div class="col-md-12">
                    <bs-input
                      :label="'Сведения о физических лицах, имеющих право действовать от имени Принципала без доверенности, срок окончания полномочий'"
                      :type="'textarea'"
                      v-model="issue.persons_can_acts_as_issuer_and_perms_term_info"
                    ></bs-input>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-12">
                    <bs-input
                      :label="'Рекомендации'"
                      :help="'Сотрудником правового управления должны быть оценена актуальность и достаточность предоставленных ' +
                        'документов (устав и изменения к нему, документы, подтверждающие полномочия руководителя (включая ' +
                        'сроки), соблюдение процедуры одобрения сделок (если подлежат одобрению по специальным основаниям). ' +
                        'Обращено внимание на соблюдение процессуальных процедур при оформлении уставных документов.'"
                      :type="'textarea'"
                      v-model="issue.lawyers_dep_recommendations"
                    ></bs-input>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-12">
                    <checkbox v-model="issue.is_positive_lawyers_department_conclusion" :type="'primary'">
                      Наличие положительного Заключения ПУ (в соответствии с Приказом по проверке ПУ)
                    </checkbox>
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
      jQuery.getJSON(this.api_url + this.$route.params.id + '/lawyers-dep-mgmt?format=json', (data, status, xhr) => {
        this.issue = data
      })
    },
    methods: {
      generate_lawyers_dep_conclusion_doc () {
        this.errors = []
        axios.post(this.api_url + this.$route.params.id + '/generate_lawyers_dep_conclusion_doc', {
          body: this.issue
        }).then(response => {
          this.update_form_data(response.data)
        }).catch(error => {
          this.errors = error.response.data.errors
        })
      },
      update_form_data (data) {
        this.issue = data
        this.errors = []
      },
      save_issue () {
        axios.post(this.api_url + this.$route.params.id + '/lawyers-dep-mgmt?format=json', {
          body: this.issue
        }).then(response => {
          this.update_form_data(response.data)
        })
      }
    }
  }
</script>
