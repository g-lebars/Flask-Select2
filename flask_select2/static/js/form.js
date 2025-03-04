(function() {
  var AdminForm = function() {
    // Field converters
    var fieldConverters = [];

    /**
    * Process AJAX+Tags fk-widget
    */
    function processAjaxWidget($el, name) {
      var tags = $el.attr('data-allow-tags') == '1';
      var multiple = $el.attr('data-multiple') == '1';
      // get tags from element

      // default to a comma for separating list items
      // allows using spaces as a token separator
      if ($el.attr('data-token-separators')) {
          var tokenSeparators = JSON.parse($el.attr('data-tags'));
      } else {
          var tokenSeparators = [';'];
      }

      // submit on ENTER
      $el.parent().find('input.select2-input').on('keyup', function(e) {
         if(e.keyCode === 13)
            $(this).closest('form').submit();
      });
      var opts = {
        width: 'resolve',
        minimumInputLength: 1,
        placeholder: 'data-placeholder',
        ajax: {
          url: $el.attr('data-url'),
          data: function(term, page) {
            return {
              query: term,
              offset: (page - 1) * 10,
              limit: 10
            };
          },
          results: function(data, page) {
            var results = [];

            for (var k in data) {
              var v = data[k];

              results.push({id: v[0], text: v[1]});
            }

            return {
              results: results,
              more: results.length == 10
            };
          }
        },
        initSelection: function(element, callback) {
          $el = $(element);
          var value = jQuery.parseJSON($el.attr('data-json'));
          var result = null;

          if (value) {
            if (multiple) {
              result = [];

              for (var k in value) {
                var v = value[k];
                result.push({id: v[0], text: v[1]});
              }

              callback(result);
            } else {
              result = {id: value[0], text: value[1]};
            }
          }

          callback(result);
        }
      };

      if (tags)
      {
          opts['createSearchChoice'] = function(term, data) {
              if ($(data).filter(function(){
                  return this.text.localeCompare(term) ===0;
              }).length ===0) {
                  return {
                      id: term,
                      text: term
                  };
              }
            };
            if(multiple){
              opts['tokenSeparators']=tokenSeparators;
              opts['formatNoMatches']= function() {
                return 'Enter comma separated values';
              };
              opts['tags']=[];
            }
    }

      if ($el.attr('data-allow-blank'))
        opts['allowClear'] = true;

      opts['multiple'] = multiple;

      $el.select2(opts);
    }

    /**
    * Process data-role attribute for the given input element. Feel free to override
    *
    * @param {Selector} $el jQuery selector
    * @param {String} name data-role value
    */
    this.applyStyle = function($el, name) {
      // Process converters first
      for (var conv in fieldConverters) {
          var fieldConv = fieldConverters[conv];

          if (fieldConv($el, name))
              return true;
      }

      // make x-editable's POST compatible with WTForms
      // for x-editable, x-editable-combodate, and x-editable-boolean cases
      var overrideXeditableParams = function(params) {
          var newParams = {};
          newParams['list_form_pk'] = params.pk;
          newParams[params.name] = params.value;
          if ($(this).data('csrf')) {
              newParams['csrf_token'] = $(this).data('csrf');
          }
          return newParams;
      }

      switch (name) {
          case 'select2':
              var opts = {
                  width: 'resolve'
              };

              if ($el.attr('data-allow-blank'))
                  opts['allowClear'] = true;

              if ($el.attr('data-tags')) {
                  $.extend(opts, {
                      tokenSeparators: [';'],
                      tags: []
                  });
              }

              $el.select2(opts);
              return true;
          case 'select2-tags':
              // get tags from element
              if ($el.attr('data-tags')) {
                  var tags = JSON.parse($el.attr('data-tags'));
              } else {
                  var tags = [];
              }

              // default to a comma for separating list items
              // allows using spaces as a token separator
              if ($el.attr('data-token-separators')) {
                  var tokenSeparators = JSON.parse($el.attr('data-tags'));
              } else {
                  var tokenSeparators = [';'];
              }

              var opts = {
                  width: 'resolve',
                  tags: tags,
                  tokenSeparators: tokenSeparators,
                  formatNoMatches: function() {
                      return 'Enter comma separated values';
                  }
              };

              $el.select2(opts);

              // submit on ENTER
              $el.parent().find('input.select2-input').on('keyup', function(e) {
                 if(e.keyCode === 13)
                    $(this).closest('form').submit();
              });
              return true;
          case 'select2-ajax':
              processAjaxWidget($el, name);
              return true;   
      }
    };


    /**
    * Apply global input styles.
    *
    * @method applyGlobalStyles
    * @param {Selector} jQuery element
    */
    this.applyGlobalStyles = function(parent) {
      var self = this;

      $(':input[data-role], a[data-role]', parent).each(function() {
          var $el = $(this);
          self.applyStyle($el, $el.attr('data-role'));
      });
    };

    /**
    * Add a field converter for customizing styles
    *
    * @method addFieldConverter
    * @param {converter} function($el, name)
    */
    this.addFieldConverter = function(converter) {
      fieldConverters.push(converter);
    };
  };

  // Add on event handler
  $('body').on('click', '.inline-remove-field' , function(e) {
      e.preventDefault();

      var form = $(this).closest('.inline-field');
      form.remove();
  });

  // Expose faForm globally
  var faForm = window.faForm = new AdminForm();

  // Apply global styles for current page after page loaded
  $(function() {
      faForm.applyGlobalStyles(document);
  });
})();
