/*****************************************************************************************************************/
/*  Author   => Albertus Restiyanto Pramayudha                                                                   */
/*  email    => xabre0010@gmail.com                                                                              */
/*  linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/                             */
/*  youtube  => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA                                         */
/*****************************************************************************************************************/

odoo.define('yudha_pnl_asset.account_report', function (require) {
'use strict';

var core = require('web.core');
var Context = require('web.Context');
var AbstractAction = require('web.AbstractAction');
var Dialog = require('web.Dialog');
var datepicker = require('web.datepicker');
var session = require('web.session');
var field_utils = require('web.field_utils');
var RelationalFields = require('web.relational_fields');
var StandaloneFieldManagerMixin = require('web.StandaloneFieldManagerMixin');
var WarningDialog = require('web.CrashManager').WarningDialog;
var Widget = require('web.Widget');
var accountReportsWidget = require('account_reports.account_report')

accountReportsWidget.include({
    render: function() {
        var self = this;
        this._super.apply(this, arguments);
        var mbody = this.$("table.o_account_reports_table.table-hover tbody");
        this.$('table.o_account_reports_table.table-hover > tbody  > tr').each(function(index, tr) {
           var nilaireport = $(this).find('span.o_account_report_column_value');
           nilaireport.each(function(){
                var cari = $(this).text().indexOf('-')
                if(cari != -1){
                    var databaru = $(this).text().replace('-','')
                    $(this).text(databaru)
                }
           });
        });
    },
})
});