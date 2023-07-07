import { Body, Controller, Post, Get, Param, Delete } from '@nestjs/common';
import { DataService } from './data.service';
import { Data } from './data.entity';
import { NewDataInput } from './data.args';
import { FindOptionsWhere } from 'typeorm';

@Controller('data')
export class DataController {
	constructor(private dataService: DataService) {}
	@Post()
	create(@Body() newDataInput: NewDataInput): Promise<Data> {
		return this.dataService.create(newDataInput);
	}

	@Get()
	findAll(): Promise<Data[]> {
		return this.dataService.findAll();
	}

	@Get()
	findOneBy(@Param('args') args: FindOptionsWhere<Data>): Promise<Data | null> {
		return this.dataService.findOneBy(args);
	}

	@Delete()
	remove(@Param('arg') arg: FindOptionsWhere<Data>): Promise<Data> {
		return this.dataService.remove(arg);
	}
}
