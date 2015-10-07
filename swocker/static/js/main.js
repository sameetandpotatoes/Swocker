$(document).ready(function(){
  $('.search').on('click', function(e){
    var company_query = $("input[type='search']").val();
    // debugger;
    // window.location.href = "/graph";
    window.location.href = "/company/"+company_query;
  });
});
