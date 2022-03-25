/*
 * jSort - jQury sorting plugin
 * http://do-web.com/jsort/overview
 *
 * Copyright 2011, Miriam Zusin
 * Dual licensed under the MIT or GPL Version 2 licenses.
 * http://do-web.com/jsort/license
 */

(function($){
   $.fn.jSort = function(options){

	var options = $.extend({
		sort_by: 'p',
		item: 'div',
		order: 'asc', //desc
		is_num: true,
		sort_by_attr: true,
		attr_name: ''
	},options);

	return this.each(function() {
		var hndl = this;
		var titles = [];
		var i = 0;

		//init titles
		$(this).find(options.item).each(function(){

			var txt;
			var sort_by = $(this).find(options.sort_by);

			if(options.sort_by_attr){
				txt = sort_by.attr(options.attr_name);
			}
			else{
				txt = sort_by.text().toLowerCase();
			}

			titles.push([txt, i]);

			$(this).attr("rel", "sort" + i);
			i++;
		});

		this.sortNum_asc = function(a, b){
			return eval(a[0] -  b[0]);
		};

		this.sortNum_desc = function(a, b){
			return eval(a[0] -  b[0]);
		};

		this.sortABC_asc = function(a, b){
			return a[0] > b[0] ? 1 : -1;
		};

		this.sortABC_desc = function(a, b){
			return a[0] > b[0] ? 1 : -1;
		};

        if(options.order == "asc"){
            if(options.is_num){
                titles.sort(hndl.sortNum_asc);
            }
            else{
                titles.sort(hndl.sortABC_asc);
            }
        }

		if(options.order == "desc"){
			if(options.is_num){
				titles.sort(hndl.sortNum_desc);
			}
			else{
				titles.sort(hndl.sortABC_desc);
			}
		}

		for (var t=0; t < titles.length; t++){
			var el = $(hndl).find(options.item + "[rel='sort" + titles[t][1] + "']");
			$(hndl).append(el);
		}

	});
   };
})(jQuery);