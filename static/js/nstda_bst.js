openerp.nstda_bst = function(instance) {

	var MODELS_TO_HIDE = [ 'nstda.bst', 'nstda.bst.hbill', 'nstda.bst.dbill' ];

	var QWeb = instance.web.qweb, _t = instance.web._t, _lt = instance.web._lt;
	var dateBefore = null;
	var get_status = {};

	instance.web.form.AbstractFormPopup
			.include({
				template : "AbstractFormPopup.render",

				setup_form_view : function() {
					var self = this;
					var tmp = this._super.apply(this, arguments);
					var res_model = this.dataset.model;

					if ($.inArray(res_model, MODELS_TO_HIDE) != -1) {
						var button_t = setInterval(
								function() {

									$(".oe_abstractformpopup-form-close")
											.addClass(
													'oe_button oe_form_button_cancel oe_highlight .openerp button.oe_highlight button.oe_highlight:hover');
									$(".oe_abstractformpopup-form-close")
											.removeClass('oe_bold');
									$(".oe_abstractformpopup-form-close").css(
											'display', 'inline-block');
									$(".oe_abstractformpopup-form-close").css(
											'line-height', '1.7em;');
									$(".oe_abstractformpopup-form-close").css(
											'background-color', 'c02c2c');
									$(".oe_abstractformpopup-form-close")
											.css('background-image',
													'-webkit-gradient(linear, left top, left bottom, from(#df3f3f), to(#a21a1a))');
									$(".oe_abstractformpopup-form-close")
											.css('background-image',
													'-webkit-linear-gradient(top, #df3f3f, #a21a1a)');
									$(".oe_abstractformpopup-form-close")
											.css('background-image',
													'-moz-linear-gradient(top, #df3f3f, #a21a1a)');
									$(".oe_abstractformpopup-form-close")
											.css('background-image',
													'-ms-linear-gradient(top, #df3f3f, #a21a1a)');
									$(".oe_abstractformpopup-form-close")
											.css('background-image',
													'-o-linear-gradient(top, #df3f3f, #a21a1a)');
									$(".oe_abstractformpopup-form-close")
											.css('background-image',
													'linear-gradient(to bottom, #df3f3f, #a21a1a)');
									$(".oe_abstractformpopup-form-close")
											.css('-moz-box-shadow',
													'0 1px 2px rgba(0, 0, 0, 0.1), 0 1px 1px rgba(155, 155, 155, 0.4) inset');
									$(".oe_abstractformpopup-form-close")
											.css('-webkit-box-shadow',
													'0 1px 2px rgba(0, 0, 0, 0.1), 0 1px 1px rgba(155, 155, 155, 0.4) inset');
									$(".oe_abstractformpopup-form-close")
											.css('box-shadow',
													'0 1px 2px rgba(0, 0, 0, 0.1), 0 1px 1px rgba(155, 155, 155, 0.4) inset');

									$(".oe_abstractformpopup-form-save").text(
											'บันทึก');
									$(".oe_abstractformpopup-form-close").text(
											'ยกเลิก');
									$(".oe_abstractformpopup-form-save-new")
											.text('บันทึก & รายการเพิ่ม');

									if ($(".oe_abstractformpopup-form-save")
											.text() == 'บันทึก')
										clearInterval(button_t);
									if ($(".oe_abstractformpopup-form-close")
											.text() == 'ยกเลิก')
										clearInterval(button_t);
									if ($(".oe_abstractformpopup-form-save-new")
											.text() == 'บันทึก & รายการเพิ่ม')
										clearInterval(button_t);
								}, 50);

					}
				}
			});

	instance.web.FormView.include({
		
		fetch: function(model, fields, domain, ctx){
            return new instance.web.Model(model).query(fields).filter(domain).context(ctx).all()
        },
		
		load_form : function() {
			var self = this;
			var tmp = this._super.apply(this, arguments);
			var res_model = this.dataset.model;
			var regex = /#id=([0-9]*)/g;
			var data = window.location.hash;
			var match = regex.exec(data);
			
			if ($.inArray(res_model, MODELS_TO_HIDE) != -1) {
				var button_t = setInterval(
						function() {
				
							if (match) {
								var id = match[1];
								self.fetch('nstda.bst.hbill',['status'],[['id','=',id]]).then(function(status){
									get_status = status;
									if(get_status){
										if (get_status[0].status == 'success') {
											$(".oe_form_button_edit").hide();
											$(".oe_form_button_edit").text('hide');
										} else {
											$(".oe_form_button_edit").show();
										}
									}
								});
							}
							if ($(".oe_form_button_edit").text() == 'hide')
								clearInterval(button_t);
						}, 50);
			}
				
//			if ($.inArray(res_model, MODELS_TO_HIDE) != -1) {
//				self.options.importable = false;
//				if (self.options.action != null) {
//					if (self.options.action.context.status == 'success') {
//						$(".oe_form_button_edit").hide();
//						this.sidebar.$el.hide();
//					} else {
//						$(".oe_form_button_edit").show();
//						this.sidebar.$el.show();
//					}
//				}
//			};
		},
	});

}