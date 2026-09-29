/*
     Author => Albertus Restiyanto Pramayudha
     email  => xabre0010@gmail.com
     linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
     youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
*/
odoo.define('yudha_payment_voucher.tree_queuebutton', function (require) {
"use strict";
     var core = require('web.core');
     var BasicController = require('web.BasicController');
     var Dialog = require('web.Dialog');
     var QWeb = core.qweb;
     var _t = core._t;
     var ListController = require('web.ListController');
     ListController.include({
        _getActionMenuItems: function (state) {
            let values = this._super.apply(this, arguments);
            if (!this.hasActionMenus || !this.selectedRecords.length) {
                return values;
            }
            if (this.modelName =='account.move') {
                values.items.other.push({
                    description: _t("Add To Queue"),
                    callback: () => {
                        Dialog.confirm(this, _t("Are you sure that you want to add to queue all the selected records?"), {
                            confirm_callback: () => this._toggleQueueRecord(),
                        });
                    }
                });
            }
            return values;

        },
        _toggleQueueRecord: async function () {
            var self = this;
            let context = this.model.get(this.handle, { raw: true }).getContext();
            const resIds = await this.getSelectedIdsWithDomain()
            const notif = this.isDomainSelected;
            var domain;
            const message = await this._rpc({
                model: 'account.move',
                method : 'get_addto_plan',
                args: [
                  resIds,
                  context,
                ]
            });
            window.location.reload()
        },
    });
});