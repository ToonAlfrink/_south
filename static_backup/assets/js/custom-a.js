// Class definition

var KTBootstrapDatepicker = function () {

    var arrows;
    if (KTUtil.isRTL()) {
     arrows = {
      leftArrow: '<i class="la la-angle-right"></i>',
      rightArrow: '<i class="la la-angle-left"></i>'
     }
    } else {
     arrows = {
      leftArrow: '<i class="la la-angle-left"></i>',
      rightArrow: '<i class="la la-angle-right"></i>'
     }
    }
   
    // Private functions
    var demos = function () {
     // minimum setup
     $('#kt_datepicker_1').datepicker({
      rtl: KTUtil.isRTL(),
      todayHighlight: true,
      orientation: "left",
      templates: arrows
     });
   
     // minimum setup for modal demo
     $('#kt_datepicker_1_modal').datepicker({
      rtl: KTUtil.isRTL(),
      todayHighlight: true,
      orientation: "bottom left",
      templates: arrows
     });
   
     // input group layout
     $('#kt_datepicker_2').datepicker({
      rtl: KTUtil.isRTL(),
      todayHighlight: true,
      orientation: "bottom left",
      templates: arrows
     });
   
     // input group layout for modal demo
     $('#kt_datepicker_2_modal').datepicker({
      rtl: KTUtil.isRTL(),
      todayHighlight: true,
      orientation: "bottom left",
      templates: arrows
     });
   
     // enable clear button
     $('#kt_datepicker_3, #kt_datepicker_3_validate').datepicker({
      rtl: KTUtil.isRTL(),
      todayBtn: "linked",
      clearBtn: true,
      todayHighlight: true,
      templates: arrows
     });
   
     // enable clear button for modal demo
     $('#kt_datepicker_3_modal').datepicker({
      rtl: KTUtil.isRTL(),
      todayBtn: "linked",
      clearBtn: true,
      todayHighlight: true,
      templates: arrows
     });
   
     // orientation
     $('#kt_datepicker_4_1').datepicker({
      rtl: KTUtil.isRTL(),
      orientation: "top left",
      todayHighlight: true,
      templates: arrows
     });
   
     $('#kt_datepicker_4_2').datepicker({
      rtl: KTUtil.isRTL(),
      orientation: "top right",
      todayHighlight: true,
      templates: arrows
     });
   
     $('#kt_datepicker_4_3').datepicker({
      rtl: KTUtil.isRTL(),
      orientation: "bottom left",
      todayHighlight: true,
      templates: arrows
     });
   
     $('#kt_datepicker_4_4').datepicker({
      rtl: KTUtil.isRTL(),
      orientation: "bottom right",
      todayHighlight: true,
      templates: arrows
     });
   
     // range picker
     $('#kt_datepicker_5').datepicker({
      rtl: KTUtil.isRTL(),
      todayHighlight: true,
      templates: arrows
     });
   
      // inline picker
     $('#kt_datepicker_6').datepicker({
      rtl: KTUtil.isRTL(),
      todayHighlight: true,
      templates: arrows
     });
    }
   
    return {
     // public functions
     init: function() {
      demos();
     }
    };
   }();
   
   jQuery(document).ready(function() {
    KTBootstrapDatepicker.init();
   });

   // SWITCH COMPONENTS

   // Class definition

var KTBootstrapSwitch = function() {

    // Private functions
    var demos = function() {
     // minimum setup
     $('[data-switch=true]').bootstrapSwitch();
    };
    
    return {
     // public functions
     init: function() {
     demos();
     },
    };
    }();
    
    jQuery(document).ready(function() {
    KTBootstrapSwitch.init();
    });

    // TEXT EDITOR

    // Class definition
var KTQuilDemos = function() {

    // Private functions
    var demo1 = function() {
        var quill = new Quill('#kt_quil_1', {
            modules: {
                toolbar: [
                    [{
                        header: [1, 2, false]
                    }],
                    ['bold', 'italic', 'underline'],
                    ['image', 'code-block']
                ]
            },
            placeholder: 'Type your text here...',
            theme: 'snow' // or 'bubble'
        });
    }

    return {
        // public functions
        init: function() {
            demo1();
            demo2();
        }
    };
}();

jQuery(document).ready(function() {
    KTQuilDemos.init();
});

// IMAGE UPLOAD

var avatar5 = new KTImageInput('kt_image_5');

avatar5.on('cancel', function(imageInput) {
 swal.fire({
  title: 'Image successfully changed !',
  type: 'success',
  buttonsStyling: false,
  confirmButtonText: 'Awesome!',
  confirmButtonClass: 'btn btn-primary font-weight-bold'
 });
});

avatar5.on('change', function(imageInput) {
 swal.fire({
  title: 'Image successfully changed !',
  type: 'success',
  buttonsStyling: false,
  confirmButtonText: 'Awesome!',
  confirmButtonClass: 'btn btn-primary font-weight-bold'
 });
});

avatar5.on('remove', function(imageInput) {
 swal.fire({
  title: 'Image successfully removed !',
  type: 'error',
  buttonsStyling: false,
  confirmButtonText: 'Got it!',
  confirmButtonClass: 'btn btn-primary font-weight-bold'
 });
});

// SELECT OPTIONS

// Class definition
var KTSelect2 = function() {
    // Private functions
    var demos = function() {
     // basic
     $('#kt_select2_1').select2({
      placeholder: "Select a state"
     });
   
     // nested
     $('#kt_select2_2').select2({
      placeholder: "Select a state"
     });
   
     // multi select
     $('#kt_select2_3').select2({
      placeholder: "Select a state",
     });
   
     // basic
     $('#kt_select2_4').select2({
      placeholder: "Select a state",
      allowClear: true
     });
   
     // loading data from array
     var data = [{
      id: 0,
      text: 'Enhancement'
     }, {
      id: 1,
      text: 'Bug'
     }, {
      id: 2,
      text: 'Duplicate'
     }, {
      id: 3,
      text: 'Invalid'
     }, {
      id: 4,
      text: 'Wontfix'
     }];
   
     $('#kt_select2_5').select2({
      placeholder: "Select a value",
      data: data
     });
   
     // loading remote data
   
     function formatRepo(repo) {
      if (repo.loading) return repo.text;
      var markup = "<div class='select2-result-repository clearfix'>" +
       "<div class='select2-result-repository__meta'>" +
       "<div class='select2-result-repository__title'>" + repo.full_name + "</div>";
      if (repo.description) {
       markup += "<div class='select2-result-repository__description'>" + repo.description + "</div>";
      }
      markup += "<div class='select2-result-repository__statistics'>" +
       "<div class='select2-result-repository__forks'><i class='fa fa-flash'></i> " + repo.forks_count + " Forks</div>" +
       "<div class='select2-result-repository__stargazers'><i class='fa fa-star'></i> " + repo.stargazers_count + " Stars</div>" +
       "<div class='select2-result-repository__watchers'><i class='fa fa-eye'></i> " + repo.watchers_count + " Watchers</div>" +
       "</div>" +
       "</div></div>";
      return markup;
     }
   
     function formatRepoSelection(repo) {
      return repo.full_name || repo.text;
     }
   
     $("#kt_select2_6").select2({
      placeholder: "Search for git repositories",
      allowClear: true,
      ajax: {
       url: "https://api.github.com/search/repositories",
       dataType: 'json',
       delay: 250,
       data: function(params) {
        return {
         q: params.term, // search term
         page: params.page
        };
       },
       processResults: function(data, params) {
        // parse the results into the format expected by Select2
        // since we are using custom formatting functions we do not need to
        // alter the remote JSON data, except to indicate that infinite
        // scrolling can be used
        params.page = params.page || 1;
   
        return {
         results: data.items,
         pagination: {
          more: (params.page * 30) < data.total_count
         }
        };
       },
       cache: true
      },
      escapeMarkup: function(markup) {
       return markup;
      }, // let our custom formatter work
      minimumInputLength: 1,
      templateResult: formatRepo, // omitted for brevity, see the source of this page
      templateSelection: formatRepoSelection // omitted for brevity, see the source of this page
     });
   
     // custom styles
   
     // tagging support
     $('#kt_select2_12_1, #kt_select2_12_2, #kt_select2_12_3, #kt_select2_12_4').select2({
      placeholder: "Select an option",
     });
   
     // disabled mode
     $('#kt_select2_7').select2({
      placeholder: "Select an option"
     });
   
     // disabled results
     $('#kt_select2_8').select2({
      placeholder: "Select an option"
     });
   
     // limiting the number of selections
     $('#kt_select2_9').select2({
      placeholder: "Select an option",
      maximumSelectionLength: 2
     });
   
     // hiding the search box
     $('#kt_select2_10').select2({
      placeholder: "Select an option",
      minimumResultsForSearch: Infinity
     });
   
     // tagging support
     $('#kt_select2_11').select2({
      placeholder: "Add a tag",
      tags: true
     });
   
     // disabled results
     $('.kt-select2-general').select2({
      placeholder: "Select an option"
     });
    }
   
    var modalDemos = function() {
     $('#kt_select2_modal').on('shown.bs.modal', function () {
      // basic
      $('#kt_select2_1_modal').select2({
       placeholder: "Select a state"
      });
   
      // nested
      $('#kt_select2_2_modal').select2({
       placeholder: "Select a state"
      });
   
      // multi select
      $('#kt_select2_3_modal').select2({
       placeholder: "Select a state",
      });
   
      // basic
      $('#kt_select2_4_modal').select2({
       placeholder: "Select a state",
       allowClear: true
      });
     });
    }
   
    // Public functions
    return {
     init: function() {
      demos();
      modalDemos();
     }
    };
   }();
   
   // Initialization
   jQuery(document).ready(function() {
    KTSelect2.init();
   });

   // CALENDAR

   var KTCalendarBasic = function() {

    return {
        //main function to initiate the module
        init: function() {
            var todayDate = moment().startOf('day');
            var YM = todayDate.format('YYYY-MM');
            var YESTERDAY = todayDate.clone().subtract(1, 'day').format('YYYY-MM-DD');
            var TODAY = todayDate.format('YYYY-MM-DD');
            var TOMORROW = todayDate.clone().add(1, 'day').format('YYYY-MM-DD');

            var calendarEl = document.getElementById('kt_calendar');
            var calendar = new FullCalendar.Calendar(calendarEl, {
                plugins: [ 'interaction', 'dayGrid', 'timeGrid', 'list' ],

                isRTL: KTUtil.isRTL(),
                header: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'dayGridMonth,timeGridWeek,timeGridDay'
                },

                height: 800,
                contentHeight: 780,
                aspectRatio: 3,  // see: https://fullcalendar.io/docs/aspectRatio

                nowIndicator: true,
                now: TODAY + 'T09:25:00', // just for demo

                views: {
                    dayGridMonth: { buttonText: 'month' },
                    timeGridWeek: { buttonText: 'week' },
                    timeGridDay: { buttonText: 'day' }
                },

                defaultView: 'dayGridMonth',
                defaultDate: TODAY,

                editable: true,
                eventLimit: true, // allow "more" link when too many events
                navLinks: true,
                businessHours: true, // display business hours
                events: [
                    {
                        title: 'All Day Event',
                        start: YM + '-01',
                        description: 'Toto lorem ipsum dolor sit incid idunt ut',
                        className: "fc-event-danger fc-event-solid-warning",
                        color: KTApp.getStateColor('info'),
                        rendering: 'background'
                    },
                    {
                        title: 'Reporting',
                        start: YM + '-14T13:30:00',
                        description: 'Lorem ipsum dolor incid idunt ut labore',
                        end: YM + '-14',
                        className: "fc-event-success"
                    },
                    {
                        title: 'Company Trip',
                        start: YM + '-02',
                        description: 'Lorem ipsum dolor sit tempor incid',
                        end: YM + '-03',
                        className: "fc-event-primary"
                    },
                    {
                        title: 'ICT Expo 2017 - Product Release',
                        start: YM + '-03',
                        description: 'Lorem ipsum dolor sit tempor inci',
                        end: YM + '-05',
                        className: "fc-event-light fc-event-solid-primary"
                    },
                    {
                        title: 'Dinner',
                        start: YM + '-12',
                        description: 'Lorem ipsum dolor sit amet, conse ctetur',
                        end: YM + '-10',
                        color: KTApp.getStateColor('info'),
                        rendering: 'background'
                    },
                    {
                        id: 999,
                        title: 'Repeating Event',
                        start: YM + '-09T16:00:00',
                        description: 'Lorem ipsum dolor sit ncididunt ut labore',
                        className: "fc-event-danger"
                    },
                    {
                        id: 1000,
                        title: 'Repeating Event',
                        description: 'Lorem ipsum dolor sit amet, labore',
                        start: YM + '-16T16:00:00',
                        color: KTApp.getStateColor('warning'),
                        rendering: 'background'
                    },
                    {
                        title: 'Conference',
                        start: YESTERDAY,
                        end: TOMORROW,
                        description: 'Lorem ipsum dolor eius mod tempor labore',
                        className: "fc-event-primary"
                    },
                    {
                        title: 'Meeting',
                        start: TODAY + 'T10:30:00',
                        end: TODAY + 'T12:30:00',
                        description: 'Lorem ipsum dolor eiu idunt ut labore',
                        color: KTApp.getStateColor('danger'),
                        rendering: 'background'
                    },
                    {
                        title: 'Lunch',
                        start: TODAY + 'T12:00:00',
                        className: "fc-event-info",
                        description: 'Lorem ipsum dolor sit amet, ut labore'
                    },
                    {
                        title: 'Meeting',
                        start: TODAY + 'T14:30:00',
                        className: "fc-event-warning",
                        description: 'Lorem ipsum conse ctetur adipi scing'
                    },
                    {
                        title: 'Happy Hour',
                        start: TODAY + 'T17:30:00',
                        className: "fc-event-info",
                        description: 'Lorem ipsum dolor sit amet, conse ctetur',
                        color: KTApp.getStateColor('danger'),
                        rendering: 'background'
                    },
                    {
                        title: 'Dinner',
                        start: TOMORROW + 'T05:00:00',
                        className: "fc-event-solid-danger fc-event-light",
                        description: 'Lorem ipsum dolor sit ctetur adipi scing'
                    },
                    {
                        title: 'Birthday Party',
                        start: TOMORROW + 'T07:00:00',
                        className: "fc-event-primary",
                        description: 'Lorem ipsum dolor sit amet, scing',
                        color: KTApp.getStateColor('danger'),
                        rendering: 'background'
                    },
                    {
                        title: 'Click for Google',
                        url: 'http://google.com/',
                        start: YM + '-28',
                        className: "fc-event-solid-info fc-event-light",
                        description: 'Lorem ipsum dolor sit amet, labore',
                        color: KTApp.getStateColor('success'),
                        rendering: 'background'
                    }
                ],

                eventRender: function(info) {
                    var element = $(info.el);

                    if (info.event.extendedProps && info.event.extendedProps.description) {
                        if (element.hasClass('fc-day-grid-event')) {
                            element.data('content', info.event.extendedProps.description);
                            element.data('placement', 'top');
                            KTApp.initPopover(element);
                        } else if (element.hasClass('fc-time-grid-event')) {
                            element.find('.fc-title').append('<div class="fc-description">' + info.event.extendedProps.description + '</div>');
                        } else if (element.find('.fc-list-item-title').lenght !== 0) {
                            element.find('.fc-list-item-title').append('<div class="fc-description">' + info.event.extendedProps.description + '</div>');
                        }
                    }
                }
            });

            calendar.render();
        }
    };
}();

jQuery(document).ready(function() {
    KTCalendarBasic.init();
});