import { Body, Controller, Post, Get, Param, Delete } from '@nestjs/common';
import { DataService } from './data.service';
import { Data } from './data.entity';
import { FindOptionsWhere } from 'typeorm';
import { DataInput } from './data.dto';

@Controller('Data')
export class DataController {
	constructor(private dataService: DataService) {}
	@Post()
	create(@Body() newData: DataInput): Promise<Data> {
		return this.dataService.createData(newData);
	}

	@Get()
	findAll(): Promise<Data[]> {
		return this.dataService.findAll();
	}

	@Get()
	findOneBy(
		@Param('args') args: FindOptionsWhere<DataInput>,
	): Promise<Data | null> {
		return this.dataService.findOneBy(args);
	}

	@Delete()
	remove(@Param('arg') arg: FindOptionsWhere<DataInput>): Promise<void> {
		return this.dataService.removeData(arg);
	}
}
