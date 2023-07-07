import { Injectable } from '@nestjs/common';
import { DeepPartial, FindOptionsWhere } from 'typeorm';
import { Data } from './data.entity';
import { DataRepository } from './data.repository';

@Injectable()
export class DataService {
	constructor(private readonly dataRepository: DataRepository) {}

	async findAll(): Promise<Data[]> {
		return await this.dataRepository.find();
	}

	async findOneBy(args: FindOptionsWhere<Data>): Promise<Data | null> {
		return await this.dataRepository.findOneBy(args);
	}

	async create(createDataInput: DeepPartial<Data>): Promise<Data> {
		const data = await this.dataRepository.createData(createDataInput);
		return await this.dataRepository.save(data);
	}

	async remove(arg: FindOptionsWhere<Data>): Promise<Data> {
		const data = await this.findOneBy(arg);
		if (data) {
			await this.dataRepository.removeData(data);
		}
		return new Data('', '', '', false);
	}
}
