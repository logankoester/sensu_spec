include_recipe 'sensu_spec'

sensu_spec "check procs" do
  command "check_procs"
  action :nothing
end.run_action(:create)

sensu_spec 'check_cmd' do
  command 'check_cmd -c "echo hi" -o "hi"'
  action :nothing
end.run_action(:create)

include_recipe 'sensu_spec::server'