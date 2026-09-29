// Author   => Albertus Restiyanto Pramayudha
// email    => xabre0010@gmail.com
// linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
// youtube  => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

odoo.define('ams_itam.restrict_button', function (require) {
"use strict";

    var FormController = require('web.FormController');
    var ListController = require('web.ListController');
    var KanbanController = require('web.KanbanController');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var ListsRender = require('web.ListRenderer')
    var _t = core._t;
    var ajax = require('web.ajax');
    var qweb = core.qweb;

    FormController.include({
        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);
        },

        renderButtons: function($node) {
            var self = this;
            this._super.apply(this, arguments);
            var context = self.model.get(self.handle, {raw: true});
            if (this.modelName =='cash.advance') {
                console.log('this state ', context['data']['state'])
                if ((context['data']['state'] !=='draft')) {
                    var tombolsave = $(this.$buttons.find('.o_form_button_edit'));
                    tombolsave.css({"display":"none"});
//                    var tomboledit = $(this.$buttons.find('.o_form_button_edit'));
//                    tomboledit.css({"display":"none"});
                }
            }
            else if (this.modelName =='settelment') {
                console.log('this state ', context['data']['state'])
                if ((context['data']['state'] !=='paid')) {
                    var tombolsave = $(this.$buttons.find('.o_form_button_edit'));
                    tombolsave.css({"display":"none"});
//                    var tomboledit = $(this.$buttons.find('.o_form_button_edit'));
//                    tomboledit.css({"display":"none"});
                }
            }
        },

    });
});