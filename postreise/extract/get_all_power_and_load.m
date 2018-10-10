function done = get_all_power_and_load(name,location,start_index,end_index)
% GET_ALL_POWER_AND_LOAD  Reads .mat files from simulation, combines it and
% saves it to csv files. One for PG and one for PF.
%   DONE = GET_ALL_POWER_AND_LOAD(NAME,LOCATION,START_INDEX,END_INDEX)
%   NAME(Name of scenario), LOCATION(Location of data),
%   START_INDEX(Start index of file to be extracted),
%   END_INDEX(End index of file to be extracted).

PG = 2;
PF = 14;

tot_out_PG = [];
tot_out_PF = [];
for k = start_index:end_index
    filename = strcat(location,name,'_sub_result_%d.mat');
    filename = sprintf(filename, k);
    data = load(filename,'mdo');
    n_intervals = size(data.mdo.flow,1);
    n_generators = size(data.mdo.flow(1).mpc.gen,1);
    n_branches = size(data.mdo.flow(1).mpc.branch,1);
    out_PG = zeros(n_generators,n_intervals);
    out_PF = zeros(n_branches,n_intervals);
    for i = (1:n_intervals)
        out_PG(:,i) = data.mdo.flow(i).mpc.gen(:,PG);
        out_PF(:,i) = data.mdo.flow(i).mpc.branch(:,PF);
    end
    tot_out_PG = [tot_out_PG,out_PG];
    tot_out_PF = [tot_out_PF,out_PF];
end

dlmwrite(strcat(location,name,'PG.csv'),tot_out_PG,'precision',12);
dlmwrite(strcat(location,name,'PF.csv'),tot_out_PF,'precision',12);
done = 1;
end