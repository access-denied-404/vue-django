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
              <div class="panel-heading">Обсуждения</div>
              <div class="panel-body">

                <div class="row">
                  <div class="col-md-12">

                    <div class="panel panel-info" v-for="message in issue.clarification_messages">
                      <div class="panel-body">
                        <div class="container-fluid">

                          <div class="row">
                            <div class="col-md-4">
                              <span class="h3">{{ message.user.last_name }} {{ message.user.first_name }}</span>
                              <div class="h4">{{ message.created_at | local_datetime }}</div>
                            </div>
                            <div class="col-md-8">
                              <div>{{ message.message }}</div>
                              <br/>
                              <div>
                                <table class="table table-condensed">
                                  <tr v-for="doclink in message.documents_links">
                                    <td>
                                      <a :href="doclink.document.file">
                                        {{ doclink.name }} <span
                                        class="glyphicon glyphicon-download-alt pull-right"></span>
                                      </a>
                                    </td>
                                  </tr>
                                </table>
                              </div>
                            </div>
                          </div>

                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="row">
                  <div class="col-md-12">
                     <form id="form_message" v-on:submit.prevent>
                       <div class="panel panel-info">
                         <div class="panel-heading">Новое сообщение</div>
                         <div class="panel-body">
                           <div class="container-fluid">

                             <div class="row">
                               <div class="col-md-12">
                                 <bs-input id="message" name="message"></bs-input>
                               </div>
                             </div>
                             <div class="row">
                               <div class="col-md-12">
                                 <div class="h4 text-center">Прикрепить документы</div>
                                 <table class="table table-condensed">
                                   <tr>
                                     <td>
                                       <input id="doc1" name="doc1" type="file">
                                     </td>
                                     <td>
                                       <input id="doc2" name="doc2" type="file">
                                     </td>
                                   </tr>
                                   <tr>
                                     <td>
                                       <input id="doc3" name="doc3" type="file">
                                     </td>
                                     <td>
                                       <input id="doc4" name="doc4" type="file">
                                     </td>
                                   </tr>
                                   <tr>
                                     <td>
                                       <input id="doc5" name="doc5" type="file">
                                     </td>
                                     <td>
                                       <input id="doc6" name="doc6" type="file">
                                     </td>
                                   </tr>
                                   <tr>
                                     <td>
                                       <input id="doc7" name="doc7" type="file">
                                     </td>
                                     <td>
                                       <input id="doc8" name="doc8" type="file">
                                     </td>
                                   </tr>
                                 </table>
                               </div>
                             </div>


                             <div class="row text-center">
                               <button class="btn btn-primary" v-on:click="send_message">Отправить</button>
                             </div>
                           </div>
                         </div>
                       </div>
                     </form>
                  </div>
                </div>

              </div>
            </div>
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
  let datetimeJsonFormat = 'YYYY-MM-DDTHH:mm'
  let dateformat = 'DD.MM.YYYY'
  let dateTimeFormat = 'DD.MM.YYYY HH:mm'

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
        message: {},
        empty_message: {
          message: ''
        }
      }
    },
    mounted: function () {
      jQuery.getJSON(this.api_url + this.$route.params.id + '/messages?format=json', (data, status, xhr) => {
        this.update_form_data(data)
      })
    },
    filters: {
      local_datetime: function (value) {
        return moment(value, datetimeJsonFormat).format(dateTimeFormat)
      }
    },
    methods: {
      update_form_data (data) {
        this.issue = data
        this.message = this.empty_message
      },
      send_message () {
//        let data = new FormData()
//        data.append('message', document.getElementById('message').value)
//        let docList = ['doc1', 'doc2', 'doc3', 'doc4', 'doc5', 'doc6', 'doc7', 'doc8']
//        for (let i = 0; i < docList.length; i++) {
//          let docName = docList[i]
//          let doc = document.getElementById(docName)
//
//          if (doc && doc.files.length) {
//            let file = doc.files[0]
//            data.append(docName, file, file.name)
//          }
//        }
//
//        axios.post(this.api_url + this.$route.params.id + '/messages', data, {
//          maxContentLength: 20000000,
//          transformRequest: [function (data, headers) {
//            return data
//          }]
//        }).then(response => {
//          this.update_form_data(response.data)
//        }).catch(function (error) {
//          console.log(error)
//        })
//        return false
      }
    }
  }
</script>
