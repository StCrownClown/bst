openerp.nstda_bst = function(instance) {

	var MODELS_TO_HIDE = [ 'nstda.bst', 'nstda.bst.hbill', 'nstda.bst.dbill' ];

	var QWeb = instance.web.qweb, _t = instance.web._t, _lt = instance.web._lt;
	var dateBefore = null;
	
	instance.web.form.AbstractFormPopup.include({
		template : "AbstractFormPopup.render",

		setup_form_view : function() {
			var self = this;
			var tmp = this._super.apply(this, arguments);
			var res_model = this.dataset.model;

			if ($.inArray(res_model, MODELS_TO_HIDE) != -1) {
				var  button_t = setInterval(function(){
					
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