openerp.nstda_bst = function(instance) {

	var MODELS_TO_HIDE = [ 'nstda.bst', 'nstda.bst.hbill', 'nstda.bst.dbill' ];

	var QWeb = instance.web.qweb, _t = instance.web._t, _lt = instance.web._lt;
	var dateBefore = null;

	instance.web.FormView.include({
		start : function() {
			var self = this;
			var ret = this._super.apply(this, arguments);
			var res_model = this.dataset.model;
			if ($.inArray(res_model, MODELS_TO_HIDE) != -1) {
				$('.oe_list_header_columns > th').css('text-align', 'center');
				self.options.importable = false;
				$(".oe_view_manager_sidebar").remove();
			}
			;
			return ret;
		},
		load_form : function() {
			var self = this;
			var tmp = this._super.apply(this, arguments);
			var res_model = this.dataset.model;

			if ($.inArray(res_model, MODELS_TO_HIDE) != -1) {
				$(document).tooltip();

				self.options.importable = false;
				$(".oe_view_manager_sidebar").remove();

				$('.oe_view_manager_buttons').show();
				$('.oe_form_button_create').show();

				var button_t = setInterval(function() {
					$('.oe_form_button').bind("click", function() {
						$(this).removeAttr('disabled');
						$(this).css('color', 'rgb(0, 0, 0)');
					});
				}, 500);

				var button_edit = setInterval(function() {
					var hedit = $('.oe_form_buttons_view').css('display');
					var form_button = "header > button.oe_form_button";
					if (hedit == 'none') {

					} else {

					}
					$("header").show();
				}, 500);

				$(document).ajaxStop(
					function() {
						var status = $(
								'.oe_form_field_status > li.oe_active')
								.attr('data-id');
						var hedit = $('.oe_form_buttons_view').css(
								'display');
						var form_button = form_button;
						if (hedit == 'none') {

						} else {

						}
					});
			}
			;
		},
	});
	
	
	instance.web.form.AbstractFormPopup.include({
		template : "AbstractFormPopup.render",

		setup_form_view : function() {
			var self = this;
			var tmp = this._super.apply(this, arguments);
			var res_model = this.dataset.model;

			if ($.inArray(res_model, MODELS_TO_HIDE) != -1) {
				var  button_t = setInterval(function(){
					$(".oe_abstractformpopup-form-save").text('xxx');
					$(".oe_abstractformpopup-form-close").text('yyy');
					$(".oe_abstractformpopup-form-save-new").text('zzz');
					
//					var attrs = { };
//					var found = $("a:contains('yyy')");
//					
//					$.each($(found)[0].attributes, function(idx, attr) {
//					    attrs[attr.nodeName] = attr.nodeValue;
//					});
//					$(found).replaceWith(function () {
//					    return $('<button class="oe_button oe_abstractformpopup-form-close oe_bold oe_highlight oe_form_button_cancel" href="javascript:void(0)" />', attrs).append($(this).contents());
//					});
					
					$(".oe_abstractformpopup-form-close").addClass('oe_button oe_form_button_cancel oe_highlight .openerp button.oe_highlight button.oe_highlight:hover');
					$(".oe_abstractformpopup-form-close").removeClass('oe_bold');
					$(".oe_abstractformpopup-form-close").css('display', 'inline-block');
					$(".oe_abstractformpopup-form-close").css('line-height', '1.7em;');
					$(".oe_abstractformpopup-form-close").css('background-color', 'c02c2c');
					$(".oe_abstractformpopup-form-close").css('background-image', '-webkit-gradient(linear, left top, left bottom, from(#df3f3f), to(#a21a1a))');
					$(".oe_abstractformpopup-form-close").css('background-image', '-webkit-linear-gradient(top, #df3f3f, #a21a1a)');
					$(".oe_abstractformpopup-form-close").css('background-image', '-moz-linear-gradient(top, #df3f3f, #a21a1a)');
					$(".oe_abstractformpopup-form-close").css('background-image', '-ms-linear-gradient(top, #df3f3f, #a21a1a)');
					$(".oe_abstractformpopup-form-close").css('background-image', '-o-linear-gradient(top, #df3f3f, #a21a1a)');
					$(".oe_abstractformpopup-form-close").css('background-image', 'linear-gradient(to bottom, #df3f3f, #a21a1a)');
					$(".oe_abstractformpopup-form-close").css('-moz-box-shadow', '0 1px 2px rgba(0, 0, 0, 0.1), 0 1px 1px rgba(155, 155, 155, 0.4) inset');
					$(".oe_abstractformpopup-form-close").css('-webkit-box-shadow', '0 1px 2px rgba(0, 0, 0, 0.1), 0 1px 1px rgba(155, 155, 155, 0.4) inset');
					$(".oe_abstractformpopup-form-close").css('box-shadow', '0 1px 2px rgba(0, 0, 0, 0.1), 0 1px 1px rgba(155, 155, 155, 0.4) inset');
					
					$(".oe_abstractformpopup-form-save").text('บันทึก');
					$(".oe_abstractformpopup-form-close").text('ยกเลิก');
					$(".oe_abstractformpopup-form-save-new").text('บันทึก & รายการเพิ่ม');
					
					if($(".oe_abstractformpopup-form-save").text() == 'บันทึก')
						clearInterval(button_t);
					if($(".oe_abstractformpopup-form-close").text() == 'ยกเลิก')
						clearInterval(button_t);
					if($(".oe_abstractformpopup-form-save-new").text() == 'บันทึก & รายการเพิ่ม')
						clearInterval(button_t);
                }, 50);
				
			}
		}		
	});
	
	
}