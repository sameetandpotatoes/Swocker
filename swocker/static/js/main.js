$(document).ready(function(){
  $('.search').on('click', function(e){
    var company_query = $("input[type='search']").val();
    window.location.href = "/company/"+company_query;
  });
});
