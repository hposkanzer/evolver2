clean:  clean_srcimgs clean_examples clean_exps clean_gallery clean_logs

clean_srcimgs:
	find srcimgs \( -name '*.html' -o -name '*.t.jpg' \) | xargs rm
	
clean_examples:
	find examples \( -name '*.html' -o -name '*.jpg' \) | xargs rm
	
clean_exps:
	find exps -type d -maxdepth 1 -mindepth 1 | grep -v exps/grid | xargs rm -r
	find exps/grid/creatures -type f | xargs rm
	
clean_gallery:
	rm gallery/*
	
clean_logs:
	find logs -name '*.log' | xargs rm
	#touch logs/evolver.log

prereqs:  	sources examples

sources:
	python ./make_sources.py --debug
	
examples:
	python ./make_examples.py --debug

EXECS=get_creatures.py \
	new_creature.py \
	new_experiment.py \
	gallery.py \
	make_examples.py \
	make_sources.py \
	hide_creature.py
	
xfer:
	rsync -auv --exclude-from ./rsync_excludes.txt . drzeus.best.vwh.net:www/htdocs/evolver2
	ssh drzeus.best.vwh.net 'cd www/htdocs/evolver2 && make bestify perms'
	
perms:
	chmod -R o+w config.json exps gallery logs
	chmod 755 ${EXECS}
	
bestify:
	perl -p -i -e 's%/usr/bin/python%/usr/local/bin/python%' ${EXECS}

unbestify:
	perl -p -i -e 's%/usr/local/bin/python%/usr/bin/python%' ${EXECS}
	
	