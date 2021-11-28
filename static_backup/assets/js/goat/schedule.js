
 function showSelection() {
    jQuery("#selection_display").empty();
    jQuery("#selection_display").append("<hr>choice  active:" + jQuery("#choice").hasClass('active'));
}

jQuery(document).ready(function () {
  jQuery(".option_group").on("click", function () {
  	 jQuery(this).toggleClass('active')
     showSelection();
     jQuery(this).toggleClass('active')
  });
  

});