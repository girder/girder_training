// Add a link to the item actions menu for starting the ITK filter job.
girder.wrap(girder.views.ItemView, 'initialize', function (initialize, settings) {
    initialize.call(this, settings);
    this.on('g:rendered', function () {
        if (girder.currentUser) {
            $(girder.templates.blur_example_itemMenu({
                item: this.model
            })).prependTo(this.$('.g-item-actions-menu'));
        }
    }, this);
});

// When the link is clicked, kick off the job, then navigate to its job details page.
girder.views.ItemView.prototype.events['click .g-blur-task-begin'] = function () {
    girder.restRequest({
        path: 'blur_example/' + this.model.id,
        type: 'POST'
    }).done(function (resp) {
        girder.router.navigate('job/' + resp._id, {trigger: true});
    });
};
